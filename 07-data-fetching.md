# فصل ۷ — Data Fetching و استراتژی‌های رندر (SSG/ISR/SSR)

> 📖 **منبع رسمی:** [nextjs.org/docs/app/building-your-application/data-fetching](https://nextjs.org/docs/app/building-your-application/data-fetching/fetching-caching-and-revalidating) — Fetching، Caching، Revalidating
> 🎯 **هدف:** چهار استراتژی رندر و *تایمینگ دقیق* انتخاب‌ها + کش در Next 16 + fetch های موازی/زنجیره‌ای.

---

## ۷.۱ — چهار استراتژی در یک جدول

| استراتژی | کِی HTML ساخته می‌شود | مناسب | چطور فعال شود |
|---|---|---|---|
| **SSG** (Static) | در build، یک بار | محتوای کم‌تغییر (لندینگ، مستندات) | پیش‌فرض! هرچی می‌تواند static است |
| **ISR** | در build + بازتولید دوره‌ای | محتوای تغییرپذیر با تحمل تأخیر (بلاگ، فروشگاه) | `revalidate = 60` |
| **SSR** (Dynamic) | هر درخواست | داده شخصی/همیشه‌تازه (داشبورد، سشن) | توابع dynamic مثل `cookies()` یا `no-store` |
| **CSR** | در مرورگر | داده واقعاً کلاینتی/لحظه‌ای | کامپوننت client + fetch/useEffect/SWR |

> 🔑 فلسفه Next 15/16: **static پیش‌فرض** — سرور خودش تشخیص می‌دهد چه چیزی صفحه را dynamic می‌کند. کار تو «اجبار» نیست، «نشان دادن قصد» است.

## ۷.۲ — آنچه صفحه را Dynamic می‌کند

این‌ها در زمان رندر استفاده شوند، صفحه dynamic می‌شود:

```tsx
import { cookies, headers } from "next/headers";

const c = (await cookies()).get("session");     // سشن = هر کاربر متفاوت
const ua = (await headers()).get("user-agent");
// و: searchParams در صفحه، fetch با cache: "no-store"
```

و برعکس، برای «تازه نگه‌داشتن بدون SSR کامل»:

```tsx
// کل صفحه بعد از ۶۰ ثانیه بازتولید:
export const revalidate = 60;

// فقط یک fetch بدون کش:
const res = await fetch(url, { cache: "no-store" });   // این fetch هر بار تازه

// یا بازاعتبارسنجی برچسب‌دار:
const res = await fetch(url, { next: { tags: ["products"] } });
revalidateTag("products");   // در Server Action بعد از mutation
```

> 💡 Next 16: سیستم کش با `use cache` و `cacheLife/cacheTag` مدرن شده — مدل ذهنی ثابت است: **cached by default، قصد را اعلام کن**؛ سینتکس‌ها را در داکیومنت چک کن.

## ۷.۳ — کجا fetch کنیم؟ (در Server Component!)

```tsx
// ✅ مستقیم در Server Component:
export default async function ProductsPage() {
  const res = await fetch("https://api.example.com/products", {
    next: { revalidate: 300 },
  });
  const products = await res.json();
  return <List items={products} />;
}
```

- بدون useEffect و بدون loading state دستی — چون سرور صبر می‌کند و HTML آماده می‌فرستد
- fetch های با URL یکسان در یک رندر **یک‌بار** زده می‌شوند (Request Memoization)
- در Client Component: فقط با SWR/TanStack یا useEffect (+محدودیت‌های فصل ۳)

### موازی در برابر زنجیره‌ای ⭐

```tsx
// ❌ زنجیره‌ای: ۲۰۰ms + ۳۰۰ms = ۵۰۰ms
const artist = await getArtist(username);
const albums = await getAlbums(artist.id);

// ✅ موازی: ۳۰۰ms
const [artist, albums] = await Promise.all([getArtist(username), getAlbums()]);
```

و اگر یکی برای رندر اولیه ضروری نیست، آن را **پایین‌تر با Suspense استریم کن** (فصل ۹):

```tsx
// بدون await — promise را پاس بده و در کامپوننت پایین‌تر با Suspense حل کن:
<Suspense fallback={<AlbumsSkeleton />}>
  <Albums promise={getAlbums()} />
</Suspense>
```

## ۷.۴ — generateStaticParams: مسیرهای دینامیک static

برای `/blog/[slug]` اگر می‌خواهی صفحات در build ساخته شوند:

```tsx
export async function generateStaticParams() {
  const posts = await getPosts();                    // لیست slug ها
  return posts.map((p) => ({ slug: p.slug }));
}
// در build: برای هر slug یک صفحه HTML
// با dynamicParams (پیش‌فرض true): slug های جدید در request ساخته و کش می‌شوند
```

ISR روی مسیرهای دینامیک هم همین‌جاست: همان `export const revalidate = 3600` — لیست‌ها و صفحات هر ساعت تازه می‌شوند.

## ۷.۵ — searchParams: فیلترهای URL

```tsx
export default async function ProductsPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string; page?: string }>;
}) {
  const { q, page = "1" } = await searchParams;   // ⚠️ Promise + رشته!
  const items = await searchProducts(q, Number(page));
}
```

نکته‌ها:
- ورود به searchParams صفحه را **dynamic** می‌کند (هر کوئری متفاوت = رندر متفاوت)
- مقادیر همیشه string اند — تبدیل کن
- تغییر searchParams از کلاینت: `router.push(\`?q=${q}\`)` — سرور دوباره رندر می‌کند و URL برای اشتراک/سئو تمیز می‌ماند (الگوی فیلتر استاندارد)

## ۷.۶ — تصویر بزرگ: کدام صفحه چه باشد؟

| صفحه | انتخاب |
|---|---|
| لندینگ | SSG خالص |
| بلاگ (لیست + پست) | SSG + ISR (`revalidate` یا webhook) |
| صفحه محصول | ISR |
| داشبورد کاربر | SSR (cookies) + استریم بخش‌های کند |
| جستجو/فیلتر | dynamic با searchParams |
| چت/تیکر زنده | SSR پوسته + CSR/SSE برای داده لحظه‌ای |

---

## ✅ جمع‌بندی فصل

- static پیش‌فرض؛ `revalidate` = ISR؛ cookies/headers/searchParams/no-store = dynamic
- fetch در Server Component؛ memoization خودکار؛ **Promise.all** برای موازی
- generateStaticParams = مسیرهای دینامیک static؛ slug های جدید خودکار کش
- searchParams: Promise + string + dynamic
- fetch سنگین دوم؟ پایین‌تر ببرش و استریم کن

## 📝 تمرین فصل ۷

1. برای هر صفحه بگو SSG/ISR/SSR/CSR و چرا: (الف) مستندات محصول (ب) سبد خرید کاربر (ج) لیست مقالات بلاگ (د) پروفایل عمومی کاربران با آواتار.
2. این صفحه چرا static رندر نمی‌شود؟
```tsx
export default async function Page() {
  const data = await fetch(url, { cache: "no-store" }).then(r => r.json());
  return <Dashboard data={data} />;
}
```
3. کد fetch زنجیره‌ای سه‌مرحله‌ای را موازی کن؛ کدام مرحله واقعاً وابسته است؟
4. چرا در Server Component از useEffect برای fetch استفاده نمی‌کنیم؟ دو دلیل.
5. فیلتر قیمت در URL (`?min=100`) — پیاده‌سازی سمت سرور و کلاینت را طراحی کن.

<details><summary>جواب‌ها</summary>

1. (الف) SSG؛ (ب) SSR (سشن/cookies)؛ (ج) SSG + ISR؛ (د) SSG/ISR (عمومی است — داده per-user نیست!).
2. `cache: "no-store"` این fetch را dynamic کرده؛ اگر می‌خواهی static بماند با تازگی: `next: { revalidate: 60 }`.
3. فقط مرحله‌ای که خروجی مرحله قبلی را می‌خواهد وابسته است؛ بقیه را با Promise.all موازی کن (و وابسته‌ها را هم می‌توان با promise پاس‌دادن + Suspense استریم کرد).
4. (۱) در Server Component داده روی سرور می‌ماند و HTML آماده می‌آید — سریع‌تر و سئو بهتر؛ (۲) waterfall و loading-state دستی حذف می‌شود + کش/memoization رایگان.
5. سرور: `const { min } = await searchParams` → فیلتر کوئری؛ کلاینت: input → `router.push(\`?min=\${v}\`)` با debounce؛ URL = منبع حقیقت فیلتر.
</details>

➡️ **فصل بعد:** Server Actions — نوشتن داده به سبک Next 16.
