# فصل ۱ — توصیف UI (Describing the UI)

> 📖 **منبع رسمی:** [react.dev/learn](https://react.dev/learn) — بخش Describing the UI
> 🎯 **هدف:** مفاهیم پایه‌ای که همه «بلدیم»، ولی در مصاحبه دقیق توضیحشان نمی‌دهیم: کامپوننت خالص، props، key ها و قواعد JSX.

---

## ۱.۱ — کامپوننت: تابعی که JSX برمی‌گرداند

```tsx
// ✅ نام با حروف بزرگ (اجباری — وگرنه JSX آن را تگ HTML می‌بیند)
function Avatar({ src, size = 40 }: { src: string; size?: number }) {
  return <img src={src} width={size} height={size} alt="" />;
}

// استفاده مثل تگ HTML:
<Avatar src="/me.png" size={64} />
```

سه قانون داکیومنت:
1. **خالص بودن (Purity):** کامپوننت نباید ورودی‌هایش را تغییر دهد یا متغیرهای بیرونی را دستکاری کند — ورودی یکسان = خروجی یکسان
2. یک کامپوننت = یک وظیفه؛ بزرگ شد بشکنش
3. فایل می‌تواند چند کامپوننت داشته باشد ولی قرارداد: یک کامپوننت اصلی هم‌نام فایل

```tsx
// ❌ ناخالص — prop را تغییر می‌دهد
function Badge({ count }: { count: number }) {
  count = count + 1;              // mutation!
  return <span>{count}</span>;
}

// ✅ خالص — از ورودی، مقدار جدید حساب می‌کند
function Badge({ count }: { count: number }) {
  return <span>{count + 1}</span>;
}
```

## ۱.۲ — JSX: قواعدی که گاهی فراموش می‌شود

| قاعده | مثال |
|---|---|
| یک root element (یا Fragment) | `<><li>۱</li><li>۲</li></>` |
| همه تگ‌ها بسته | `<img />` |
| تقریباً همه attribute ها camelCase | `className`، `onClick`، `tabIndex` |
| `{}` = ورود به دنیای JS | `{user.name}`، `{isAdmin && <Admin/>}` |
| استایل = آبجکت | `style={{ marginTop: 8 }}` |
| کامنت داخل JSX | `{/* مثل این */}` |

**Conditional rendering — چهار الگوی داکیومنت:**

```tsx
{isPacked && "✅"}                      // && — اگر true
{isPacked ? "✅" : "⬜"}                // ternary — دو حالت
{error != null && <ErrorBox msg={error} />}  // ⚠️ حواست به 0!
{status === "loading" ? <Spinner/> : <Content/>}
```

> ⚠️ **تله کلاسیک `&&`:** اگر سمت چپ عدد `0` شود، React خودِ `0` را رندر می‌کند!
> `{items.length && <List/>}` ← وقتی لیست خالی است، روی صفحه **0** می‌بینی!
> علاج: `{items.length > 0 && <List/>}` یا ternary.

## ۱.۳ — Props: فقط خواندنی و یک‌طرفه

- Props از **پدر به فرزند** جاری می‌شوند — فرزند هرگز نمی‌تواند prop پدر را عوض کند (one-way data flow)
- «تغییر props» در React ضدالگو است — تغییر باید با state باشد و در کامپوننتی که مالک آن است انجام شود
- `children` = prop ویژه: هرچی بین تگ باز و بسته بنویسی

```tsx
function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="card">
      <h3>{title}</h3>
      {children}          {/* هر JSX ای که والد داخلش گذاشت */}
    </div>
  );
}
```

## ۱.۴ — لیست‌ها و Key: پرتکرارترین سوال مصاحبه ⭐

```tsx
const todos = [
  { id: 10, text: "خرید" },
  { id: 22, text: "مطالعه" },
];

<ul>
  {todos.map((t) => (
    <li key={t.id}>{t.text}</li>    {/* key = شناسه پایدار */}
  ))}
</ul>
```

**key برای چیست؟** React برای اینکه بداند کدام آیتم اضافه، حذف یا جابجا شده، بین رندرها آیتم‌ها را با key تطبیق می‌دهد. key درست یعنی state و DOM هر آیتم درست حفظ می‌شوند.

| key | داوری |
|---|---|
| `id` پایدار از داده | ✅ استاندارد |
| **index آرایه** | ⚠️ فقط اگر: لیست ثابت است، هرگز reorder/sort نمی‌شود، وسطش insert نمی‌شود |
| `Math.random()` | ❌ هر رندر عوض می‌شود — فاجعه برای performance و state |

> 🔑 مثال کلاسیک خرابی: لیست با key={index} که آیتم اولش حذف می‌شود → همه key ها شیفت می‌شوند → React فکر می‌کند محتوای هر ردیف عوض شده → state اینپوت‌ها به ردیف‌های اشتباه می‌چسبد!

## ۱.۵ — رندر: چی اتفاق می‌افتد؟

چرخه هر رندر: **Trigger (setState / اولین mount) → Render (صدا زدن کامپوننت‌ها) → Commit (به‌روزرسانی DOM)**

- رندر یعنی «صدا زدن تابع کامپوننت» — نباید عوارض جانبی داشته باشد
- React در StrictMode در dev هر کامپوننت را **دو بار** صدا می‌زند تا ناخالصی‌ها را لو بدهد — عادی است، باگ نیست!

---

## ✅ جمع‌بندی فصل

- کامپوننت = تابع خالص با حرف بزرگ که JSX برمی‌گرداند
- `{}` برای JS؛ `&&` با ۰ تله دارد؛ یک root
- props فقط‌خواندنی و یک‌طرفه؛ children = محتوای داخل تگ
- key = شناسه پایدار؛ index فقط برای لیست‌های کاملاً ثابت
- رندر = صدا زدن تابع؛ StrictMode عمداً دو بار صدا می‌زند

## 📝 تمرین فصل ۱

1. این کامپوننت سه ایراد دارد — پیدا کن:
```tsx
function UserCard(user) {
  user.name = user.name.toUpperCase();
  return <div className=user-card>{user.name}</div>;
}
```
2. `{count && <Badge count={count} />}` چه زمانی خروجی عجیب می‌دهد؟ درستش کن.
3. لیست کاربران قابل sort است — آیا `key={index}` مجاز است؟ چرا؟
4. StrictMode چرا در dev کامپوننت‌ها را دو بار رندر می‌کند و در production چرا نه؟

<details><summary>جواب‌ها</summary>

1. (۱) props را mutate می‌کند (ناخالص) — `user.name.toUpperCase()` را در متغیر جدید بریز و همان را رندر کن؛ (۲) `user` به‌صورت prop نام‌گذاری‌شده نیامده — باید `{ user }: { user: User }` باشد؛ (۳) `className=user-card` بدون کوتیشن و آکولاد نوشته شده — درستش `className="user-card"` است.
2. وقتی `count = 0` است — JS مقدار `0` را برمی‌گرداند و React عدد ۰ را رندر می‌کند. درست: `{count > 0 && <Badge count={count} />}`.
3. نه — چون sort ترتیب را عوض می‌کند و key های index با آیتم‌ها تطبیق داده نمی‌شوند؛ state و DOM به هم می‌ریزند. از `user.id` استفاده کن.
4. برای کشف side-effect ها (ناخالصی)؛ چون در production این چک هزینه دارد و فرض بر این است که کد ناخالصی ندارد.
</details>

➡️ **فصل بعد:** مدیریت State — snapshot ها، آپدیت immutable و الگوهای سازمان‌دهی.
