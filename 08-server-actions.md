# فصل ۸ — Server Actions و Mutations

> 📖 **منبع رسمی:** [nextjs.org/docs/app/building-your-application/updating-data](https://nextjs.org/docs/app/building-your-application/updating-data/fetching-updating-and-revalidating-data) — Updating Data، Server Actions and Mutations
> 🎯 **هدف:** نوشتن داده بدون API endpoint دستی: تعریف، اتصال به فرم، اعتبارسنجی، بازاعتبارسنجی کش (revalidate) و اتصال به هوک‌های فرم ۱۹ (فصل ۴).

---

## ۸.۱ — Server Action: تابع async با `"use server"`

```ts
// app/actions.ts
"use server";                       // کل فایل = همه توابع سروری

import { revalidatePath } from "next/cache";
import { db } from "@/lib/db";

export async function createPost(formData: FormData) {
  const title = String(formData.get("title") ?? "").trim();
  const body = String(formData.get("body") ?? "").trim();

  if (!title) return { error: "عنوان الزامی است" };   // برگشت به کلاینت

  await db.post.create({ data: { title, body } });

  revalidatePath("/blog");          // کش لیست را باطل کن
  return { ok: true };
}
```

چیزی که اتفاق می‌افتد: Next.js از این تابع یک **endpoint RPC خودکار** می‌سازد — کلاینت فقط reference تابع را دارد، بدنه روی سرور اجرا می‌شود (دیتابیس و secret امن‌اند).

دو محل تعریف: فایل جدا با `"use server"` بالای فایل، یا inline داخل کامپوننت کلاینت (`async function () { "use server"; ... }`).

## ۸.۲ — اتصال به فرم (سه سطح)

**سطح ۱ — مستقیم در فرم Server Component** (ساده‌ترین):

```tsx
export default function NewPostPage() {
  async function addPost(formData: FormData) {
    "use server";
    // ... ذخیره ...
    revalidatePath("/blog");
  }
  return (
    <form action={addPost}>
      <input name="title" required />
      <textarea name="body" />
      <button>ثبت</button>
    </form>
  );
}
```

بدون یک خط fetch/state — progressive enhancement هم دارد (با JS غیرفعال هم کار می‌کند!).

**سطح ۲ — با useActionState: نتیجه و ارور به کاربر:**

```tsx
"use client";
import { useActionState } from "react";
import { createPost } from "@/app/actions";

const [state, formAction, isPending] = useActionState(createPost, { error: null });

<form action={formAction}>
  <input name="title" />
  {state.error && <p className="text-red-600">{state.error}</p>}
  <button disabled={isPending}>{isPending ? "..." : "ثبت"}</button>
</form>
```

(امضای اکشن در این حالت `(prevState, formData)` است — prevState آرگومان اول می‌آید!)

**سطح ۳ — بدون فرم: صدا زدن مستقیم:**

```tsx
<button onClick={() => deletePost(id)}>حذف</button>   // Server Action در onClick ✅
```

(فقط داخل event handler یا transition — نه در حین رندر.)

## ۸.۳ — بازاعتبارسنجی: کش بعد از نوشتن

بعد از هر mutation، داده‌های کش‌شده قدیمی‌اند — باطلشان کن:

```ts
revalidatePath("/blog");          // کل مسیر
revalidatePath("/blog/[slug]", "page");   // همه صفحات داینامیک
revalidateTag("posts");           // همه fetch هایی که tag "posts" دارند
```

| ابزار | scope | کی |
|---|---|---|
| `revalidatePath("/blog")` | یک مسیر | تغییر محلی |
| `revalidateTag("posts")` | همه‌ی داده‌های برچسب‌خورده | mutation روی یک موجودیت (تمیزتر!) |
| `redirect("/blog/42")` | ناوبری بعد از اکشن | بعد از ساخت رکورد |

با `next: { tags: ["posts"] }` در fetch ها (فصل ۷) جفتشان کن — الگوی استاندارد: **نوشتن → revalidateTag → UI تازه.**

## ۸.۴ — اعتبارسنجی ورودی: همیشه سرور ⭐

کلاینت قابل دورزدن است — Server Action خط دفاعی واقعی است:

```ts
import { z } from "zod";

const PostSchema = z.object({
  title: z.string().min(3).max(120),
  body: z.string().min(1),
});

export async function createPost(prevState: any, formData: FormData) {
  const parsed = PostSchema.safeParse(Object.fromEntries(formData));
  if (!parsed.success) {
    return { error: parsed.error.issues[0].message, values: Object.fromEntries(formData) };
  }
  // ذخیره...
}
```

(zod — همان که در دوره‌های Next و وردپرس استفاده کردی. در پروژه واقعی، چک auth و ownership هم به همین‌جا اضافه می‌شود.)

## ۸.۵ — ریزه‌کاری‌های مهم

- **سریال‌سازی به معنی امنیت نیست:** Server Action هر ورودی‌ای می‌پذیرد — اعتماد نکن؛ validate و authorization را خودت انجام بده (مثل `where: { id, userId }` دوره‌های قبل)
- **محدودیت حجم body پیش‌فرض ۱MB** — برای آپلود فایل، `serverActions.bodySizeLimit` یا مسیر Route Handler
- **Sequential:** اکشن‌های یک فرم صف می‌شوند؛ برای چند اکشن همزمان: `useTransition` + صدا زدن مستقیم
- **Cookie/redirect در اکشن:** `cookies()` قابل ست‌کردن است و `redirect()` وسط اکشن مجاز (خطای NEXT_REDIRECT داخلی است — try/catch آن را بلع نکن!)

## ۸.۶ — جانشین‌ها: کی Server Action، کی Route Handler؟

| | Server Action | Route Handler (`route.ts`) |
|---|---|---|
| فرم‌ها و mutations از UI خود سایت | ⭐ بهترین انتخاب | قابل استفاده |
| API عمومی (موبایل، third-party، webhook) | ❌ | ⭐ تنها راه |
| پاس JSON خام با کنترل هدر | نه | ⭐ |

---

## ✅ جمع‌بندی فصل

- `"use server"` + تابع async = endpoint خودکار امن سمت سرور
- فرم: action={serverAction} → useActionState برای state/ارور/pending → useFormStatus در فرزند
- بعد از نوشتن: **revalidateTag/Path** — وگرنه UI قدیمی می‌ماند
- اعتبارسنجی با zod همیشه سرور؛ auth هم همین‌جا
- API عمومی = Route Handler، نه Server Action

## 📝 تمرین فصل ۸

1. فرم «افزودن محصول» کامل بساز: اکشن سرور + zod + ارور + pending + revalidateTag("products") — و fetch لیست با همان tag.
2. چرا `redirect("/blog")` داخل `try { ... } catch { }` اکشن، ارور عجیب می‌دهد؟
3. سناریوی حذف با تأیید: دکمه‌ی حذف در لیست (Server Component) است — چطور Server Action را صدا می‌زنی و تأیید (confirm) را کجا می‌گذاری؟
4. مشتری موبایل می‌خواهد همان «ساخت پست» را از اپ خودش بزند — چه تغییر معماری؟

<details><summary>جواب‌ها</summary>

1. (اسکلت پیشنهادی) اکشن سروری با zod و برگشت `{ error }` در شکست؛ بعد از ذخیره `revalidateTag("products")`؛ فرم کلاینی با useActionState و دکمه‌ای که `isPending` دارد؛ و fetch لیست با `next: { tags: ["products"] }` تا با همان تگ تازه شود.
2. redirect با پرتاب یک خطای خاص NEXT_REDIRECT کار می‌کند — catch عمومی آن را می‌بلعد. علاج: redirect را خارج از try بگذار یا در catch نوع خطا را re-throw کن.
3. حذف یک mutation است: یک کامپوننت کلاینی کوچک `DeleteButton` با `confirm()` مرورگر و `useTransition` می‌سازیم؛ داخل `startTransition` اکشن سروری `deletePost(id)` را صدا می‌زنیم و کش با `revalidatePath` تازه می‌شود.
4. یک Route Handler (`app/api/posts/route.ts`) برای اپ موبایل — همان اعتبارسنجی zod را در یک ماژول مشترک بین Action و Handler نگه دار (DRY).
</details>

➡️ **فصل بعد:** Streaming و مدیریت ارور — loading/error/not-found.
