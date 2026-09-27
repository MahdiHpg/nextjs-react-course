# فصل ۱۱ — Route Handler، Middleware و Deployment

> 📖 **منبع رسمی:** [nextjs.org/docs/app/building-your-application/routing/route-handlers](https://nextjs.org/docs/app/building-your-application/routing/route-handlers) + Middleware + Deploying
> 🎯 **هدف:** لایه API خود Next.js (Route Handler)، لایه بین‌راهی (Middleware)، متغیرهای محیطی در دو دنیای سرور/کلاینت، و نکات دپلوی Vercel/self-host.

---

## ۱۱.۱ — Route Handler: API داخل خود Next

```ts
// app/api/products/route.ts
import { NextRequest, NextResponse } from "next/server";

export async function GET(req: NextRequest) {
  const q = req.nextUrl.searchParams.get("q") ?? "";
  const products = await db.product.findMany({ where: { title: { contains: q } } });
  return NextResponse.json(products);
}

export async function POST(req: NextRequest) {
  const body = await req.json();
  const product = await db.product.create({ data: body });
  return NextResponse.json(product, { status: 201 });
}

// و دینامیک: app/api/products/[id]/route.ts
export async function DELETE(req: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;                 // ⚠️ باز هم Promise!
  await db.product.delete({ where: { id: Number(id) } });
  return new NextResponse(null, { status: 204 });
}
```

- همان الگوی Express-ish ولی فایل‌محور؛ متدهای HTTP = export های هم‌نام
- وابستگی‌های request: `req.nextUrl`، هدرها، cookies
- **Caching:** GET به‌صورت پیش‌فرض در build کش می‌شود اگر static باشد — برای dynamic شدن: از `req` استفاده کن یا `export const dynamic = "force-dynamic"` (یا در fetch های داخلی no-store)
- **استریم و webhook:** برای چک امضای webhook ها (مثل درگاه پرداخت)، بدنه‌ی خام را با `await req.text()` بخوان

### کی Route Handler و کی Server Action؟ (تکرار از فصل ۸ — یک‌خطی)

**مصرف‌کننده خارج از مرورگر خودت (موبایل/webhook/third-party) → Handler؛ فرم و UI خود سایت → Server Action.**

## ۱۱.۲ — Middleware: نگهبان بین‌راه

`middleware.ts` در ریشه — قبل از هر request (و completion بعد از آن) اجرا می‌شود؛ روی edge سبک است. ⚠️ **به‌روزرسانی Next.js 16:** نام این فایل به `proxy.ts` تغییر کرده و به‌طور پیش‌فرض روی **Node.js runtime** اجرا می‌شود؛ فایل قدیمی `middleware.ts` هنوز پشتیبانی می‌شود و مثل قبل روی edge اجرا می‌شود. مفهوم «edge» را در [فصل ۱۳](./13-faq-deep-dive.md) عمیق بخوان:

```ts
import { NextRequest, NextResponse } from "next/server";

export function middleware(req: NextRequest) {
  const session = req.cookies.get("session");

  // محافظت از مسیرها:
  if (!session && req.nextUrl.pathname.startsWith("/dashboard")) {
    return NextResponse.redirect(new URL("/login", req.url));
  }

  // افزودن هدر:
  const res = NextResponse.next();
  res.headers.set("x-frame-options", "DENY");
  return res;
}

export const config = {
  matcher: ["/dashboard/:path*", "/admin/:path*"],   // فقط این مسیرها
};
```

کاربردهای متعارف: auth-redirect، A/B با rewrite، افزودن هدرهای امنیتی، i18n (تشخیص زبان). ⚠️ کار سنگین نکن — روی هر request اجرا می‌شود؛ اتصال دیتابیس اینجا ممنوع است.

## ۱۱.۳ — Environment Variables: دو دنیا

```bash
# .env.local
DATABASE_URL="postgresql://..."        # فقط سرور ✅
STRIPE_SECRET="sk_..."                 # فقط سرور ✅
NEXT_PUBLIC_API_URL="https://api.site.com"   # ⚠️ به کلاینت هم می‌رود!
```

| پیشوند | کجا در دسترس | خطر |
|---|---|---|
| بدون پیشوند | فقط Server Component / Action / Route Handler | امن برای رازها |
| `NEXT_PUBLIC_` | + باندل کلاینت | **راز هرگز!** چون داخل JS ساخته‌شده embed می‌شود |

قواعد: `.env*` در gitignore؛ روی Vercel/سرور از پنل Environment Variables؛ `process.env` فقط سمت سرور در زمان اجرا خوانده می‌شود (NEXT_PUBLIC ها در build اینلاین می‌شوند).

## ۱۱.۴ — دپلوی

### Vercel (ساده‌ترین و کامل‌ترین برای App Router)

```bash
npx vercel            # یا: import از GitHub در پنل
```

- هر push به main → production deploy؛ هر PR → preview URL
- ISR/Caching/Image Optimization همه managed
- Env vars را در پنل ست کن (Local ≠ production!)
- Server Actions و SSR به serverless function نیاز دارند — خودکار مدیریت می‌شود

### Self-host (سرور خودت — دوره Docker!)

```bash
# سرور:
docker run -d -p 3000:3000 --restart unless-stopped \
  -e DATABASE_URL="..." myapp:1.0
# پشت nginx/caddy برای SSL و دامنه؛ با استانداردهای فصل ۱۲ دوره داکر:
# healthcheck، بکاپ دیتابیس، prune، log ها
```

نکته self-host: ISR/Cache روی دیسک/Redis؛ Image Optimization تنظیم می‌خواهد (`images.unoptimized` یا سرویس جدا) — Vercel این‌ها را رایگان حل کرده؛ انتخاب بین این دو، انتخابی معماری است.

## ۱۱.۵ — چک‌لیست Production

- [ ] env های production در پنل پلتفرم؛ هیچ رازی با NEXT_PUBLIC_
- [ ] `metadataBase` ست شده (برای URL های OG)
- [ ] ارورها مانیتور می‌شوند (Sentry و...) — digest ها بی‌معنا بدون لاگ
- [ ] `middleware` matcher دقیق — نه catch-all سنگین
- [ ] API ها: rate limit + auth (فصل ۸)
- [ ] تست: build لوکال `next build` بدون ارور type/ESLint قبل از push

---

## ✅ جمع‌بندی فصل

- Route Handler = API فایل‌محور؛ Server Action برای UI خودت، Handler برای دنیای بیرون
- Middleware = نگهبان سبک edge با matcher دقیق (auth/هدر)
- env: بدون پیشوند = سرور؛ NEXT_PUBLIC_ = در باندل کلاینت embed — راز هرگز
- Vercel = صفر پیکربندی؛ self-host = داکر + nginx + مسئولیت ISR/cache

## 📝 تمرین فصل ۱۱

1. `GET /api/orders?status=paid` با فیلتر و pagination (هدر X-Total-Count) بنویس — و بگو چرا اینجا Server Action جوابگو نبود.
2. Middleware بنویس: کاربر بدون کوکی session از `/admin/*` به `/login?next=<مسیر فعلی>` برود و بعد از لاگین برگردد.
3. چرا `NEXT_PUBLIC_DB_PASSWORD` یک فاجعه است حتی اگر «فقط برای تست» باشد؟
4. مقایسه دپلوی: پروژه‌ات را به Vercel ببر (env ها را یادت نرود) — یا اگر VPS داری، با دانش داکری‌ات طرح self-host بنویس (نه کد — معماری).

<details><summary>جواب‌ها</summary>

1. Server Action برای مصرف‌کننده‌های خارج از اپ (موبایل/webhook) قابل فراخوانی مستقیم نیست و کنترل هدر/status کاستوم ندارد — Handler استاندارد API عمومی است.
2. 
```ts
export function middleware(req: NextRequest) {
  if (!req.cookies.get("session")) {
    const url = new URL("/login", req.url);
    url.searchParams.set("next", req.nextUrl.pathname);
    return NextResponse.redirect(url);
  }
}
export const config = { matcher: ["/admin/:path*"] };
```
3. چون همه‌چیزِ NEXT_PUBLIC_ در فایل‌های JS ساخته‌شده embed می‌شود — هرکسی View Source بزند رمز دیتابیس را می‌بیند؛ «تست» هم یک روز production می‌شود.
4. Vercel: import ریپو + env ها؛ Self-host: image اپ + network داکر به دیتابیس + caddy برای SSL + بکاپ cron + `revalidate` روی دیسک — مسئولیت‌های Vercel را خودت می‌پذیری.
</details>

➡️ **فصل آخر:** چیت‌شیت دوتایی + گلاساری + ۲۰ سوال مصاحبه.
