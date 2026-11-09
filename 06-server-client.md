# فصل ۶ — Server vs Client Components ⭐ (قلب App Router)

> 📖 **منبع رسمی:** [nextjs.org/docs/app/building-your-application/rendering](https://nextjs.org/docs/app/building-your-application/rendering/server-components) — Server and Client Components، Composition Patterns
> 🎯 **هدف:** مهم‌ترین فصل برای مصاحبه و مهم‌ترین منبع باگ‌های روزمره — مدل ذهنی کامل RSC: کی سرور، کی کلاینت، مرزها و ترکیب‌ها.

---

## ۶.۱ — مدل ذهنی: پیش‌فرض سرور است

در App Router **همه‌چیز به صورت پیش‌فرض Server Component است** — نه چون «سرور رندر می‌کند»؛ بلکه چون کد آن **فقط روی سرور اجرا می‌شود و خروجی‌اش (RSC payload) به مرورگر می‌رود**:

| | Server Component (پیش‌فرض) | Client Component (`"use client"`) |
|---|---|---|
| اجرا | فقط سرور (یک بار در build/request) | سرور (SSR اولیه) **+ مرورگر (hydrate/interactivity)** |
| JS فرستاده به کلاینت | ❌ صفر | ✅ کدش می‌رود |
| دیتابیس/فایل/secret | ✅ مستقیم | ❌ هرگز |
| useState/useEffect/hooks مرورگری | ❌ ندارد | ✅ دارد |
| onClick/onSubmit | ❌ کار نمی‌کند | ✅ |
| async/await در خودش | ✅ مستقیم | ❌ (با useEffect/use یا پدر سرور) |

> 🔑 جمله قاب‌شدنی: **«Client Component یعنی interactive است، نه اینکه فقط در کلاینت اجرا شود.»** — اولین رندرش هم روی سرور HTML می‌شود.

## ۶.۲ — مرز: `"use client"` یعنی «درِ زیر من کلاینتی»

directive روی اول فایل، **تمام import های آن فایل** را کلاینت می‌کند — مرز، یک‌طرفه از آن نقطه به پایین است:

```
app/page.tsx (Server) ✅
└── FilterPanel.tsx ("use client") 🧊 کلاینتی
    └── FilterList.tsx 🧊 کلاینتی (بدون directive هم کلاینتی است — زیر مرز!)
    └── DataService.ts ❌ import آن به RSC کار نمی‌کند
```

پیامدها:
- یک کامپوننت کلاینی نمی‌تواند async باشد و مستقیم دیتابیس بخواند
- اما می‌تواند زیر خودش، کامپوننت **سروری** را به عنوان children دریافت کند! (بخش ۶.۴)

## ۶.۳ — پاس دادن داده از سرور به کلاینت: Serialization ⭐

مرز سرور→کلاینت یک «مرز سریال‌سازی» است — فقط داده‌های serializable رد می‌شوند:

| رد می‌شود ✅ | رد نمی‌شود ❌ |
|---|---|
| آبجکت/آرایه/رشته/عدد/بولین/null | توابع |
| Date، Map، Set، Promise (RSC) | کلاس‌های با متد/behavior |
| React Element (JSX) | import شدن مستقیم کامپوننت سروری در فایل کلاینی |

```tsx
// ✅ Server Component:
<ProductCard product={product} />      // آبجکت ساده ✅
<Chart getData={loadData} />           // ❌ تابع — cross نمی‌شود!
```

## ۶.۴ — Composition: پترن‌های طلایی ⭐

الگوی «کلاینت به قدر لزوم» — تا جای ممکن پایین درخت کلاینت کن:

```tsx
// ✅ Server (page.tsx):
<ClientInteractivePiece data={serializable} />
```

و **الگوی children/passthrough** — وقتی کامپوننت کلاینی می‌خواهد «چیزی سروری» را نشانت بدهد:

```tsx
// ❌ اشتباه رایج: کلاینت نمی‌تواند <ServerOnlyStuff/> را import کند
"use client";
function Sidebar() {
  return <div>{/* می‌خواهم اینجا ServerChart بگذارم */}</div>;
}

// ✅ درست: کامپوننت‌های سروری به عنوان children/props از پدر سروری:
// page.tsx (Server):
<Sidebar>
  <ServerChart />       ← هنوز سروری است! فقط از داخل کلاینی «عبور» داده شد
</Sidebar>

// Sidebar.tsx ("use client"):
function Sidebar({ children }: { children: React.ReactNode }) {
  return <aside>{children}</aside>;   // children را فقط نمایش می‌دهد
}
```

چرا کار می‌کند؟ چون ServerChart **قبل از رسیدن به مرز** روی سرور رندر شده و به‌صورت خروجی رندرشده از داخل props عبور کرده است.

### Context و سرور

Provider ها (ThemeContext و...) چون state دارند کلاینتی‌اند — الگوی استاندارد: خود Provider را کلاینت کن ولی children را از سرور بگیر:

```tsx
// theme-provider.tsx ("use client") — فقط منطق context
export function ThemeProvider({ children }) { ... }

// layout.tsx (Server):
<ThemeProvider>{children}</ThemeProvider>   // کل درخت سروری زیرش می‌ماند ✅
```

## ۶.۵ — کی کدام؟ (جدول تصمیم)

| کامپوننت | باشد |
|---|---|
| داده می‌گیرد (db، API، فایل) | Server |
| secret / کلید API مصرف می‌کند | Server |
| وابستگی سنگین (دیتاویز، ادیتور) | Server (اگر تعاملی نیست) — باندل صفر! |
| state / effect / رویداد / browser API | Client |
| Context مصرف می‌کند | Client |

قاعده عملی: **از Server شروع کن؛ فقط جایی که interactivity لازم شد، یک جزیره کلاینت کوچک بساز** — و آن جزیره را تا جای ممکن پایینِ درخت ببر.

## ۶.۶ — عوارض جانبی مرز (که فقط با تجربه می‌فهمی)

| علامت | علت | علاج |
|---|---|---|
| `useState is not a function in Server Component` | hook در کامپوننت سروری | یا `"use client"` یا تقسیم کامپوننت |
| `Event handlers cannot be passed to Client Component props` | پاس دادن تابع به کلاینت از سرور | تابع را داخل کامپوننت کلاینی تعریف کن یا Server Action بده (فصل ۸) |
| یک کتابخانه کلاینتی کل صفحه را کلاینت کرد | directive در فایل بالادستی | مرز را پایین ببر — فایل ورودی کلاینی کوچک بساز |
| props با تابع: `Functions cannot be passed...` | serialization | Server Action (فصل ۸) یا داده به جای تابع |

---

## ✅ جمع‌بندی فصل

- پیش‌فرض = Server؛ کدش به کلاینت نمی‌رود؛ db/secret فقط آنجا
- `"use client"` = مرز یک‌طرفه به پایین؛ کلاینت = SSR اولیه + interactivity
- مرز = serializable: داده ✅، تابع ❌ (به‌جز Server Actions)
- children/passthrough = عبور کامپوننت سروری از میان کلاینی
- Provider کلاینی با children سروری — الگوی استاندارد
- جزیره‌های کلاینی کوچک، پایین درخت

## 📝 تمرین فصل ۶

1. کدام فایل‌ها کلاینتی‌اند؟ (فقط اسم بگو)
```
A.tsx  (بدون directive، useState دارد؟ نه — فقط fetch دیتابیس)
B.tsx  ("use client" در بالا، <C/> را رندر می‌کند)
C.tsx  (بدون directive، فقط div استاتیک)
D.tsx  (از A import می‌شود؛ onClick دارد بدون directive)
```
2. چرا این کد ارور می‌دهد و دو راه‌حل؟
```tsx
// page.tsx (Server)
<DatePicker onChange={(d) => saveDate(d)} />
```
3. کامپوننت کلاینی می‌خواهد داده دیتابیس را نمایش دهد — سه راه درست را بگو (بدون اتصال مستقیم دیتابیس از کلاینت).
4. سناریو: یک صفحه سروری + یک «ناوبری تب‌های محلی» (state دار) + محتوای هر تب سروری رندر می‌شود — طراحی کن.

<details><summary>جواب‌ها</summary>

1. A سروری (بدون hook)؛ B کلاینی (directive)؛ C کلاینی (زیر مرز B — هرچند استاتیک است و اگر از A فراخوانی می‌شد می‌توانست سروری بماند)؛ D کلاینی است به شرطی که داخل B مصرف شود (onClick در درخت کلاینی کار می‌کند). اگر D مستقیم از A صدا شود → ارور.
2. تابع از سرور به کلاینت پاس نمی‌شود (serialization). راه ۱: DatePicker کلاینی باشد و onChange را داخل خودش با Server Action صدا بزند؛ راه ۲: Server Action به عنوان prop (فصل ۸ — Server Action ها قابل پاس شدن از سرور به کلاینت‌اند!).
3. (۱) خود کامپوننت سروری بماند و داده را بگیرد، فقط بخش تعاملی‌اش کلاینی؛ (۲) Route Handler + fetch در کلاینت؛ (۳) Server Action و برگرداندن داده.
4. layout/page سروری → محتوای هر تب را به عنوان آرایه‌ای از ReactNode آماده کند → `<Tabs serverContent={[{label, node}, ...]} />` کلاینی فقط state تب فعال را نگه دارد و node مربوطه را رندر کند — الگوی children/passthrough.
</details>

➡️ **فصل بعد:** Data Fetching — SSG/ISR/SSR و تایمینگ دقیق‌شان.
