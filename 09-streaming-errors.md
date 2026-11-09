# فصل ۹ — Streaming و مدیریت ارور

> 📖 **منبع رسمی:** [nextjs.org/docs/app/building-your-application/routing](https://nextjs.org/docs/app/building-your-application/routing/loading-ui-and-streaming) — Loading UI، Error Handling
> 🎯 **هدف:** صفحه را تکه‌تکه و تدریجی بفرست (Streaming) و برای هر لایه، مرز خطای خودش را بساز — `loading.tsx`، `<Suspense>`، `error.tsx`، `not-found.tsx`.

---

## ۹.۱ — Streaming: پوسته اول، بقیه بعداً

مشکل: صفحه‌ای با دو کوئری — یکی ۵۰ms و یکی ۲ ثانیه. بدون streaming کاربر ۲ ثانیه صفحه سفید می‌بیند. جواب: HTML پوسته را فوری بفرست و بخش کند را وقتی حاضر شد تزریق کن:

```tsx
// app/dashboard/page.tsx
import { Suspense } from "react";

export default function DashboardPage() {
  return (
    <div>
      <h1>داشبورد</h1>                        ← فوری ارسال می‌شود
      <section>
        <Stats />                              ← سریع — همراه پوسته
      </section>
      <Suspense fallback={<RevenueSkeleton />}>
        <Revenue />                            ← کند — استریم می‌شود
      </Suspense>
      <Suspense fallback={<ChartSkeleton />}>
        <SlowChart />                          ← کندتر — استریم مستقل
      </Suspense>
    </div>
  );
}

async function Revenue() {
  const data = await getRevenue();   // کند — اما بقیه صفحه قفل نمی‌شود
  return <p>{data.total.toLocaleString("fa-IR")}</p>;
}
```

هر Suspense مستقل استریم می‌شود و fallback هر بخش جداگانه جایگزین می‌شود. **داده کند را پایین ببر و استریم کن؛ کل صفحه را گروگان نکن.**

## ۹.۲ — loading.tsx: Suspense خودکار برای کل مسیر

```tsx
// app/dashboard/loading.tsx
export default function Loading() {
  return <DashboardSkeleton />;
}
```

معادل پیچیدن کل `page.tsx` آن مسیر در Suspense است — در ناوبری‌ها فوراً نمایش داده می‌شود. (همچنین `layout.tsx` را ثابت نگه می‌دارد — nav گیر نمی‌کند.) می‌توانی آن را در هر عمق بگذاری تا فقط زیرشاخه‌ی زیرش skeleton بگیرد.

> 💡 loading.tsx و Suspense دو ابزار یک هدف‌اند: فایل مخصوص = پوشش کل مسیر؛ Suspense = دانه‌ریز به دلخواه تو.

## ۹.۳ — error.tsx: مرز خطا

اگر در حین رندر اروری پرتاب شود (کوئری شکست‌خورده و...)، نزدیک‌ترین `error.tsx` همان بخش را نشان می‌دهد و بقیه صفحه زنده می‌ماند:

```tsx
// app/dashboard/error.tsx
"use client";                        // ⚠️ اجباری — کامپوننت کلاینت

export default function DashboardError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;                 // تلاش دوباره — رندر همان بخش
}) {
  return (
    <div className="p-6 border border-red-300 rounded-xl bg-red-50">
      <h2>مشکلی پیش آمد!</h2>
      <button onClick={reset}>تلاش دوباره</button>
    </div>
  );
}
```

نکته‌ها:

- error.tsx **کلاینت** است؛ برای لاگ سمت سرور از `global-error.tsx` یا onError استفاده کن — و پیام خام ارور را به کاربر نشان نده (digest برای پشتیبانی)
- `error.tsx` ارورهای **event handler ها و Server Action ها** را نمی‌گیرد — آن‌ها را خودت با try/catch مدیریت کن
- `global-error.tsx` (در ریشه، کنار layout) = آخرین مرز — باید خودش `<html>` و `<body>` داشته باشد
- `unhandledRejection` در Next 15+ خودش به مرزها می‌رسد (unstable_rethrow برای catch های عمومی اکشن‌ها)

## ۹.۴ — notFound(): 404 کنترل‌شده

```tsx
// در هر Server Component:
import { notFound } from "next/navigation";

const post = await getPost(slug);
if (!post) notFound();               // → نزدیک‌ترین not-found.tsx + status 404

// app/blog/[slug]/not-found.tsx — پیام اختصاصی همان بخش
// app/not-found.tsx — 404 سراسری
```

تفاوت با throw new Error: notFound یک «حالت مورد انتظار» است (رکوردی که دنبالش بودی وجود ندارد) — 404 تمیز می‌دهد، نه صفحه ارور.

## ۹.۵ — الگوی صفحه production (جمع همه)

```tsx
export default async function ProductPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;

  const product = await getProduct(id);       // ضروری — بالا
  if (!product) notFound();

  return (
    <main>
      <ProductHeader product={product} />     ← فوری
      <Suspense fallback={<ReviewsSkeleton />}>
        <Reviews id={id} />                   ← کند — استریم + ارور محلی
      </Suspense>
    </main>
  );
}
// error.tsx کنارش: ارور فقط بخش را می‌گیرد
```

---

## ✅ جمع‌بندی فصل

- استریم = پوسته فوری + تزریق تدریجی؛ `<Suspense>` دانه‌ریز، `loading.tsx` مسیری
- بخش کند را پایین درخت ببر، کل صفحه را گروگان نگیر
- error.tsx = مرز ارور (کلاینت!) + reset؛ global-error آخرین مرز
- ارورهای event/action را خودت catch کن
- `notFound()` = 404 مورد انتظار با پیام اختصاصی

## 📝 تمرین فصل ۹

1. صفحه با ۴ بخش دارد (هدر، آمار سریع، لیست کند، نمودار بسیار کند) — طرح استریمش را بنویس و بگو کدام‌ها داخل Suspense اند و چرا.
2. چرا error.tsx باید `"use client"` باشد؟ (راهنمایی: ارور کی و کجا مدیریت می‌شود؟)
3. تفاوت رفتار: throw در Server Component هنگام رندر، vs پرتاب در Server Action هنگام submit؟
4. `not-found.tsx` کجاها فعال می‌شود؟ (سه مورد)
5. (کد) یک `loading.tsx` اسکلتی با انیمیشن pulse برای کارت‌های ۳-ستونه بنویس.

<details><summary>جواب‌ها</summary>

1. هدر و آمار سریع همراه پوسته می‌آیند؛ لیست کند و نمودار بسیار کند هرکدام داخل `<Suspense>` با fallback خودشان قرار می‌گیرند — چون کندتر از بقیه‌اند و نباید نمایش بقیه را نگه دارند.
2. چون error.tsx در مرورگر هم اجرا می‌شود (نمایش پیام/دکمه reset در حین ناوبری کلاینتی) — رفتار تعاملی نیاز به کامپوننت کلاینت دارد؛ ارور از سرور serialize شده به آن می‌رسد.
3. throw در حین رندر → نزدیک‌ترین error.tsx همان بخش؛ پرتاب در Server Action → به catch سمت کلاینتِ صدا زننده می‌رسد (مثلاً state.error در useActionState) — مرز error.tsx آن را نمی‌گیرد.
4. (۱) فراخوانی `notFound()` در همان بخش؛ (۲) مسیری که match نشد؛ (۳) URL دستکاری‌شده خارج از پارامترهای مجاز — همه به نزدیک‌ترین not-found.tsx می‌روند.
5. 
```tsx
export default function Loading() {
  return (
    <div className="grid grid-cols-3 gap-4 animate-pulse">
      {Array.from({ length: 6 }).map((_, i) => (
        <div key={i} className="h-40 bg-gray-200 rounded-xl" />
      ))}
    </div>
  );
}
```
</details>

➡️ **فصل بعد:** بهینه‌سازی — Image، Font، Metadata.
