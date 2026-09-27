# فصل ۴ — React 19 و پترن‌های مدرن

> 📖 **منبع رسمی:** [react.dev/reference/react](https://react.dev/reference/react) — use، useActionState، useFormStatus، useOptimistic، useTransition
> 🎯 **هدف:** هوک‌های نسل جدید React 19 که Next.js 16 روی آن‌ها سوار است — مخصوصاً سه‌گانه‌ی فرم‌ها که در فصل ۸ دوباره به کارت می‌آید.

---

## ۴.۱ — useTransition: رندر غیر‌فوری (Non-blocking)

آپدیت «کند» (فیلتر لیست بزرگ) را کم‌اولویت کن تا UI فوری (اینپوت) گیر نکند:

```tsx
const [isPending, startTransition] = useTransition();

function onChange(e: React.ChangeEvent<HTMLInputElement>) {
  setQuery(e.target.value);                    // فوری: اینپوت روان می‌ماند
  startTransition(() => {
    setFiltered(hugeFilter(e.target.value));   // کم‌اولویت: قابل قطع
  });
}

{isPending && <SpinnerMini />}
```

`useDeferredValue(value)` معادل ساده‌ترش است — نسخه‌ی عقب‌مانده‌ی value را می‌دهد تا React اول UI فوری را رندر کند.

## ۴.۲ — use: خواندن Promise و Context با شرط

هوک جدید که برخلاف بقیه می‌تواند **داخل شرط و حلقه** صدا زده شود:

```tsx
import { use } from "react";

function Comments({ commentsPromise }: { commentsPromise: Promise<Comment[]> }) {
  const comments = use(commentsPromise);   // Suspense را فعال می‌کند تا promise حل شود
  return comments.map((c) => <Comment key={c.id} {...c} />);
}

// والد: promise را می‌سازد و می‌فرستد + <Suspense> برای حالت بارگذاری
<Comments commentsPromise={fetchComments()} />
```

همچنین جایگزین useContext است: `const theme = use(ThemeContext);`

> 💡 این همان الگویی است که Server Component های Next.js با prop ی از جنس promise استفاده می‌کنند (مثل فصل ۹ دوره وردپرس Headless).

## ۴.۳ — useActionState: فرم + state نتیجه اکشن

جایگزین مدرن چرخه‌ی «submit → loading → نتیجه/ارور»:

```tsx
const [state, formAction, isPending] = useActionState(
  async (prevState, formData) => {
    const name = String(formData.get("name") ?? "");
    const error = name.trim() ? null : "نام الزامی است";
    if (error) return { error };
    await saveName(name);
    return { ok: true };
  },
  { error: null }
);

<form action={formAction}>
  <input name="name" />
  {state.error && <p className="text-red-600">{state.error}</p>}
  <button disabled={isPending}>{isPending ? "..." : "ذخیره"}</button>
</form>
```

پیش‌فرض در Next.js: وقتی action یک Server Action باشد (فصل ۸)، همین الگو رواج دارد.

## ۴.۴ — useFormStatus: حالت فرم از داخل فرزند

دکمه‌ی submit معمولاً در کامپوننت جداست و به state فرم دسترسی ندارد — این هوک همان فرم پدر را می‌خواند:

```tsx
function SubmitButton() {
  const { pending } = useFormStatus();     // ⚠️ باید داخل <form> باشد
  return <button disabled={pending}>{pending ? "در حال ارسال..." : "ثبت"}</button>;
}

<form action={formAction}>
  <input name="name" />
  <SubmitButton />
</form>
```

## ۴.۵ — useOptimistic: به‌روزرسانی خوش‌بینانه

قبل از جواب سرور، UI را آپدیت کن — اگر شکست خورد، به حالت قبلی برمی‌گردد:

```tsx
const [optimisticLikes, addOptimistic] = useOptimistic(likes, (cur, delta: number) => cur + delta);

async function handleLike() {
  addOptimistic(1);                          // فوری در UI دیده می‌شود
  await likePost(postId);                    // درخواست واقعی
  startTransition(() => { refreshLikes(); }); // همگام‌سازی نهایی با سرور
}
```

تجربه‌ی UX اینستاگرامی: لایک فوری، همگام‌سازی پشت صحنه.

## ۴.۶ — ref به عنوان prop + ref cleanup (React 19)

از ۱۹ به بعد دیگر `forwardRef` لازم نیست — `ref` یک prop معمولی است:

```tsx
function MyInput({ ref, ...props }: { ref?: React.Ref<HTMLInputElement> }) {
  return <input ref={ref} {...props} />;
}
// و cleanup ref: برگرداندن تابع از callback ref (جدید در ۱۹)
<input ref={(node) => { register(node); return () => unregister(node); }} />
```

## ۴.۷ — چیزهای دیگر ۱۹ در یک نگاه

| قابلیت | چیست |
|---|---|
| `use server` / `use client` | directive ها (پایه Server Actions فصل ۸) |
| Server Components پایدار | در Next.js از قبل استفاده می‌کردی |
| بهبود hydration errors | پیام ارور با diff واقعی DOM |
| `<Context>` به جای Provider | `<ThemeContext value={theme}>` |
| Document metadata | `<title>`/`<meta>` در کامپوننت‌ها (در Next.js با Metadata API بهتر است — فصل ۱۰) |

---

## ✅ جمع‌بندی فصل

- `useTransition`/`useDeferredValue` = آپدیت کند، UI روان
- `use` = خواندن promise/context در هر جایی (Suspense-friendly)
- سه‌گانه فرم: **useActionState** (نتیجه)، **useFormStatus** (pending از فرزند)، **useOptimistic** (UX فوری)
- ref به عنوان prop معمولی؛ خداحافظی با forwardRef
- memo کردن: اندازه‌گیری‌شده — React Compiler در راه است

## 📝 تمرین فصل ۴

1. تفاوت useTransition و useDeferredValue را با یک مثال بگو — کی هرکدام؟
2. چرا useActionState سه عضو برمی‌گرداند و نقش هرکدام؟
3. سناریو: در چت، پیام کاربر بلافاصله در لیست بیاید و ارسال در پس‌زمینه انجام شود — کدام هوک؟ اسکلت کد بنویس.
4. `useFormStatus` را در کامپوننتی خارج از `<form>` صدا زدی — چه می‌بینی و چرا؟

<details><summary>جواب‌ها</summary>

1. useTransition: آپدیت‌های «خودم اجرا می‌کنم» را کم‌اولویت می‌کند (نوشتن منطق)؛ useDeferredValue: مقدار را «دیرتر» می‌دهد وقتی نمی‌خواهی منطق را دستکاری کنی (فقط مصرف‌کننده کند است). برای فیلتر حین تایپ هر دو؛ برای prop دریافتی فقط deferred.
2. `state` (خروجی آخرین اکشن)، `formAction` (برای action فرم)، `isPending` (در حال اجرا بودن اکشن).
3. useOptimistic:
```tsx
const [optimisticMessages, addOptimistic] = useOptimistic(messages,
  (cur, msg: Message) => [...cur, { ...msg, pending: true }]);
async function send(text: string) {
  const msg = { id: crypto.randomUUID(), text };
  addOptimistic(msg);
  await postMessage(msg);
  startTransition(() => { refresh(); });
}
```
4. همیشه `pending: false` — چون useFormStatus به نزدیک‌ترین `<form>` والدش (در همان درخت رندر) وصل است؛ بیرون فرم، فرمی برای خواندن نمی‌بیند.
</details>

➡️ **بخش دوم — Next.js 16:** از این‌جا به بعد روی App Router سوار می‌شویم.
