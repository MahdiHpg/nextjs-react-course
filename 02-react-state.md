# فصل ۲ — مدیریت State (Managing State)

> 📖 **منبع رسمی:** [react.dev/learn/managing-state](https://react.dev/learn/managing-state) + Reference: useState، useReducer، useContext
> 🎯 **هدف:** state به عنوان snapshot، آپدیت immutable، batching، و انتخاب درست بین useState / useReducer / Context.

---

## ۲.۱ — State یک snapshot است (پرتکرارترین سوءتفاهم)

```tsx
function handleClick() {
  setCount(count + 1);
  setCount(count + 1);
  setCount(count + 1);
  // مقدار نمایش داده‌شده: +۱ فقط! چرا؟
}
```

`count` یک **متغیر عادی در این رندر** است — در هر سه خط، همان مقدار رندر فعلی خوانده می‌شود. setState = «درخواست رندر با مقدار جدید»، نه تغییر فوری متغیر.

**علاج: آپدیت تابعی** — وقتی به state قبلی وابسته‌ای:

```tsx
function handleClick() {
  setCount((c) => c + 1);   // ✅ سه بار = +۳
  setCount((c) => c + 1);
  setCount((c) => c + 1);
}
```

قاعده طلایی: **اگر state جدید از state قبلی محاسبه می‌شود، همیشه فرم تابعی بزن.**

## ۲.۲ — Batching: چند setState در یک event

React 18+ همه setState های یک event handler را در **یک رندر** جمع می‌کند (batching) — حتی داخل setTimeout و promise ها. پس نگران «سه setState = سه رندر» نباش.

## ۲.۳ — Immutable Update: فراموش نکردنی‌ها ⭐

state اشیاء و آرایه‌ها را **جایگزین کن، نه تغییر بده** — چون React با مرجع (reference) تغییر را تشخیص می‌دهد:

```tsx
// ❌ mutation — React متوجه تغییر نمی‌شود
user.name = "Ali";
setUser(user);
cart.push(item);
setCart(cart);

// ✅ immutable — آبجکت/آرایه جدید
setUser({ ...user, name: "Ali" });
setCart([...cart, item]);

// آپدیت تودرتو با spread زنجیره‌ای:
setUser({
  ...user,
  address: { ...user.address, city: "تهران" },
});

// حذف و آپدیت در آرایه:
setTodos(todos.filter((t) => t.id !== id));
setTodos(todos.map((t) => (t.id === id ? { ...t, done: true } : t)));
```

> 💡 برای ساختارهای عمیق، Immer یا ابزارهای مدیریت state سروری مثل TanStack Query این درد را می‌گیرند — ولی اصل را باید بلد باشی.

## ۲.۴ — Lifting State Up: بردن state به مشترک‌ترین جد

دو کامپوننت خواهر به داده مشترک نیاز دارند؟ state را به **نزدیک‌ترین پدر مشترک** ببر و با props پایین بده:

```tsx
function SearchPage() {
  const [query, setQuery] = useState("");       // اینجا بالای هر دو
  return (
    <>
      <SearchBox value={query} onChange={setQuery} />
      <ResultList query={query} />
    </>
  );
}
```

سرچ‌باکس «controlled» است: مقدارش از props می‌آید (single source of truth).

## ۲.۵ — useReducer: وقتی منطق پیچیده می‌شود

وقتی چند فیلد state با هم مرتبط‌اند و transition های مشخصی دارند، reducer منطق را متمرکز می‌کند:

```tsx
type State = { items: CartItem[]; total: number };
type Action =
  | { type: "add"; item: CartItem }
  | { type: "remove"; id: number }
  | { type: "clear" };

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case "add":
      return {
        items: [...state.items, action.item],
        total: state.total + action.item.price,
      };
    case "remove": {
      const item = state.items.find((i) => i.id === action.id)!;
      return {
        items: state.items.filter((i) => i.id !== action.id),
        total: state.total - item.price,
      };
    }
    case "clear":
      return { items: [], total: 0 };
  }
}

const [state, dispatch] = useReducer(reducer, { items: [], total: 0 });
dispatch({ type: "add", item: newOne });
```

| useState | useReducer |
|---|---|
| state مستقل و ساده | چند state مرتبط / منطق پیچیده |
| آپدیت‌ها پراکنده در کامپوننت | همه transition ها در یک تابع قابل‌تست |

## ۲.۶ — Context: رد کردن props از وسط درخت

مشکل «prop drilling»: داده باید از ۵ لایه عبور کند. Context یعنی پخش سراسری:

```tsx
const ThemeContext = createContext<"light" | "dark">("light");

// در بالای درخت:
<ThemeContext.Provider value={theme}>
  <App />
</ThemeContext.Provider>

// در هر عمقی:
const theme = useContext(ThemeContext);
```

⚠️ دو هشدار داکیومنت:
1. Context برای **داده‌های کم‌تغییر** (تم، locale، کاربر جاری) است — نه state پرتغییر (هر تغییر = رندر همه مصرف‌کننده‌ها)
2. قبل از Context، اول lifting را امتحان کن؛ بسیاری از دریلینگ‌ها با composition (children) حل می‌شوند

## ۲.۷ — دو قانون دیفرنسینگ state (از داکیومنت)

1. **State هایی که همیشه با هم تغییر می‌کنند را یکی کن** — دو state `firstName/lastName` که همیشه با هم ست می‌شوند → یکی `fullName`
2. **چیزهایی که از state دیگر محاسبه می‌شوند را state نکن** — `filtered = items.filter(...)` محاسبه کن، state نگیر (وگرنه دوتا منبع حقیقت!)

---

## ✅ جمع‌بندی فصل

- state = snapshot رندر فعلی؛ آپدیت وابسته → فرم تابعی `(c) => ...`
- batching: چند setState = یک رندر
- immutable: با spread و الگوهای filter/map؛ هرگز mutation
- lifting state up؛ controlled components؛ composition قبل از Context
- useReducer برای ماشین‌حالت‌های پیچیده
- state محاسبه‌شدنی = محاسبه، نه state

## 📝 تمرین فصل ۲

1. خروجی چیست و چرا؟
```tsx
const [age, setAge] = useState(20);
<button onClick={() => { setAge(age + 1); setAge(age + 1); }}>+</button>
```
2. کد سبد خرید زیر باگ state دارد — درستش کن:
```tsx
function addToCart(item: Item) {
  cart.items.push(item);
  setCart(cart);
}
```
3. یک فرم با سه state جدا (`name`, `email`, `message`) که همیشه با هم reset می‌شوند — پیشنهاد داکیومنت چیست؟
4. چه زمانی useReducer به جای چند useState به کار می‌آید؟ یک مثال واقعی از پروژه‌هایت بنویس.

<details><summary>جواب‌ها</summary>

1. فقط +۱ — هر دو فراخوانی از snapshot همان رندر می‌خوانند. درست: `setAge(a => a + 1)` دوبار.
2. mutation آرایه و پاس دادن همان مرجع → React rerender نمی‌کند. درست: `setCart({ ...cart, items: [...cart.items, item] })`.
3. یکی‌کردن: یک آبجکت `form` با یک `setForm` + آپدیت immutable (`setForm({...form, name: v})`) یا یک state `emptyForm` برای reset.
4. مثال: state سبد خرید با add/remove/clear/qty-change — transition های مشخص، منطق متمرکز و قابل تست.
</details>

➡️ **فصل بعد:** Escape Hatches — useRef، useEffect و جادوهای پشت درِ شماره ۳.
