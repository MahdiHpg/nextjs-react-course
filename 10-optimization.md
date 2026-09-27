# فصل ۱۰ — بهینه‌سازی: Image، Font، Metadata

> 📖 **منبع رسمی:** [nextjs.org/docs/app/building-your-application/optimizing](https://nextjs.org/docs/app/building-your-application/optimizing/images) — Optimizing بخش‌ها
> 🎯 **هدف:** سه بهینه‌ساز داخلی که امتیاز Lighthouse و Core Web Vitals سایتت را می‌سازند: next/image، next/font و Metadata API.

---

## ۱۰.۱ — next/image: تصویر هوشمند

```tsx
import Image from "next/image";
import hero from "@/public/hero.jpg";      // import = اندازه خودکار!

// Static import (پیشنهادی — سایز خودش می‌داند):
<Image src={hero} alt="صفحه اصلی" priority placeholder="blur" />

// Remote:
<Image src="https://cdn.site.com/pic.jpg"
       alt="محصول" width={800} height={450}
       sizes="(max-width: 768px) 100vw, 50vw" />
```

چه چیزهایی مجانی می‌گیری:

| قابلیت | اثر |
|---|---|
| بهینه‌سازی/فرمت مدرن (WebP/AVIF) + resize on demand | حجم چند برابر کمتر |
| Lazy load پیش‌فرض | صفحه اول سبک |
| جلوگیری از layout shift (نیاز به width/height یا fill) | CLS صفر |
| `priority` | Preload برای LCP (تصویر اول صفحه!) |

پرچم‌های مهم:

- **`priority`** — روی تصویر بالای فولد (hero) بزن؛ باقی lazy می‌مانند
- **`sizes`** — به مرورگر بگو تصویر در چه عرض‌هایی نمایش داده می‌شود تا مناسب‌ترین نسخه را بگیرد؛ بدون آن، تصویر بزرگ‌تر از نیاز دانلود می‌شود
- **`fill`** + پدر با `position:relative` — برای تصاویر full-width با object-fit
- **`placeholder="blur"`** — فقط با static import (blurDataURL خودکار)

عکس‌های دامنه خارجی → `remotePatterns` در next.config (در فصل ۱۲ دوره وردپرس دیدی!).

**اصل طلایی:** تصویر اول (LCP) = `priority` + `sizes` درست؛ بقیه = lazy پیش‌فرض.

## ۱۰.۲ — next/font: فونت بدون CLS و بدون درخواست اضافه

```tsx
// app/layout.tsx
import { Vazirmatn } from "next/font/google";

const vazir = Vazirmatn({
  subsets: ["arabic"],
  variable: "--font-vazir",
  display: "swap",
});

export default function RootLayout({ children }) {
  return (
    <html lang="fa" dir="rtl" className={vazir.variable}>
      <body>{children}</body>
    </html>
  );
}
```

```css
/* tailwind/css */
font-family: var(--font-vazir);
```

مزایا نسبت به `<link>` گوگل‌فونت:

- فونت در **build دانلود و self-host** می‌شود — بدون درخواست به گوگل در runtime (حریم + سرعت + بدون FOUT کلاسیک)
- `display: swap` — متن فوری با فونت جایگزین، بعد تعویض
- `variable: --font` — مصرف تمیز در Tailwind/CSS
- فایل‌های لوکال هم: `next/font/local`

## ۱۰.۳ — Metadata API: سئو بدون فایل‌های جدا

```tsx
// static:
export const metadata: Metadata = {
  title: "فروشگاه دیجی",
  description: "بهترین gadgets بازار",
  openGraph: { images: ["/og.png"] },
};

// dynamic — در صفحه جزئیات:
export async function generateMetadata({ params }): Promise<Metadata> {
  const { slug } = await params;
  const post = await getPost(slug);
  return {
    title: post.title,
    description: post.excerpt,
    alternates: { canonical: `/blog/${slug}` },
    openGraph: {
      title: post.title,
      images: post.featuredImage?.sourceUrl ? [post.featuredImage.sourceUrl] : [],
    },
  };
}
```

- metadata هنگام رندر ارزیابی و در `<head>` تزریق می‌شود — همه روی سرور
- قالب‌بندی با `title.template` در layout والد: `"%s | دیجی"` — فرزند فقط title بدهد
- فایل‌های قراردادی: `app/icon.png` (فاویکون)، `app/opengraph-image.tsx` (تصویر OG تولیدشده با کد!)، `sitemap.ts`، `robots.ts`

```ts
// app/sitemap.ts — سایت‌مپ داینامیک از دیتابیس:
export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const posts = await getPosts();
  return [
    { url: "https://site.com", changeFrequency: "daily", priority: 1 },
    ...posts.map((p) => ({ url: `https://site.com/blog/${p.slug}`, lastModified: p.date })),
  ];
}
```

(این دقیقاً همان چیزی است که در دوره وردپرس Headless برای سئو استفاده کردی — حالا روش رسمی‌اش را می‌دانی.)

## ۱۰.۴ — بهینه‌سازی‌های دیگر (یک نگاه)

| ابزار | کار |
|---|---|
| `next/script` | بارگذاری اسکریپت third-party با استراتژی (`afterInteractive`) |
| `next/dynamic` | import lazy کامپوننت (کد سنگین مثل ادیتور) — `ssr: false` برای browser-only |
| Bundle Analyzer | `@next/bundle-analyzer` — کی باندل سنگین شد؟ |
| `experimental.optimizePackageImports` | tree-shake بهتر آیکون‌لایبرری‌ها |

---

## ✅ جمع‌بندی فصل

- Image: بهینه‌سازی + lazy + CLS صفر؛ hero → priority/sizes؛ خارجی → remotePatterns
- Font: self-host در build با next/font — بدون درخواست خارجی، با swap
- Metadata: static/dynamic + template + فایل‌های قراردادی (icon/og/sitemap/robots)
- dynamic import برای کد سنگین؛ اسکریپت‌ها با next/script

## 📝 تمرین فصل ۱۰

1. صفحه‌ای با یک hero بزرگ بالای فولد و ۱۲ کارت عکس‌دار — هر تصویر چه تنظیمی می‌خواهد؟ (priority/sizes/fill?)
2. چرا `<Image src="https://cdn.x.com/a.jpg" />` بدون width/height یا fill ارور می‌دهد؟ این اجبار چه چیزی را تضمین می‌کند؟
3. تفاوت `display: swap` و فونت بدون swap از نظر تجربه کاربر و CLS؟
4. `generateMetadata` بنویس که title را از قالب والد بگیرد (`%s | شاپ`) و og:image از تصویر شاخص پست.
5. (تحقیق) `opengraph-image.tsx` را امتحان کن — تصویر اشتراک‌گذاری توییتر را با کد تولید کن (ImageResponse).

<details><summary>جواب‌ها</summary>

1. hero: `priority` + `sizes="100vw"` + placeholder (اگر static import)؛ کارت‌ها: بدون priority (lazy) + `sizes="(max-width: 768px) 100vw, 33vw"` + width/height یا fill با پدر relative.
2. اجبار به ابعاد = جلوگیری از layout shift (CLS) — مرورگر از قبل فضا رزرو می‌کند؛ با `fill` هم پدر باید ابعاد داشته باشد.
3. swap: متن فوری با فونت سیستمی سپس تعویض (FOUT — متن همیشه دیده می‌شود)؛ بدون swap: صفحه تا لود فونت متن را مخفی می‌کند (FOIT) — CLS و تأخیر ادراکی بدتر.
4. 
```tsx
export async function generateMetadata({ params }): Promise<Metadata> {
  const { slug } = await params;
  const post = await getPost(slug);
  return {
    title: post.title,                                  // با template والد
    openGraph: { images: post.image ? [post.image] : [] },
  };
}
```
</details>

➡️ **فصل بعد:** Route Handler ها، Middleware، env و دپلوی.
