# فصل ۳ — Escape Hatches: useRef، useEffect و Custom Hooks

> 📖 **منبع رسمی:** [react.dev/learn/escape-hatches](https://react.dev/learn/escape-hatches) + Reference: useRef، useEffect، useMemo، useCallback
> 🎯 **هدف:** دم به درِ سه — خروج از جریان رندر: دسترسی به DOM، همگام‌سازی با دنیای بیرون، و یادگیری اینکه useEffect «چرخه عمر» نیست بلکه **همگام‌ساز** است.

---

## ۳.۱ — useRef: جعبه‌ای که رندر نمی‌شود

ref = یک ظرف mutable که **بین رندرها حفظ می‌شود ولی تغییرش رندر ایجاد نمی‌کند**:

```tsx
const inputRef = useRef<HTMLInputElement>(null);

<input ref={inputRef} />
<button onClick={() => inputRef.current?.focus()}>فوکوس</button>
```

دو کاربرد اصلی:
1. **DOM** — فوکوس، scrollIntoView، اندازه‌گیری
2. **مقدار بی‌رندر** — timer id، شمارنده‌ی بین رندرها، previous value

```tsx
const renderCount = useRef(0);
renderCount.current++;      // تغییرش رندر نمی‌سازد — فقط ذخیره
```

| | state | ref |
|---|---|---|
| تغییر → رندر؟ | ✅ بله | ❌ نه |
| خواندن در رندر؟ | بله (snapshot) | ❌ نباید در رندر خوانده شود |
| مناسب | داده نمایشی | مقدار فنی/DOM |

## ۳.۲ — useEffect: همگام‌سازی با دنیای بیرون

مهم‌ترین بازتعریف داکیومنت: **Effects برای همگام‌سازی با سیستم‌های بیرونی‌اند** (سرور، subscription، API های DOM که React مدیریتشان نمی‌کند)، نه برای منطق عادی:

```tsx
useEffect(() => {
  const conn = createConnection(roomId);   // با سیستم بیرون همگام شو
  conn.connect();
  return () => conn.disconnect();          // cleanup: همگام‌سازی قبلی را قطع کن
}, [roomId]);                              // وقتی roomId عوض شد
```

**چرخه ذهنی درست:** تغییر prop/state → رندر → DOM آپدیت → **اگر وابستگی عوض شده، cleanup قبلی + effect جدید**

### وابستگی‌ها (dependencies)

- آرایه خالی `[]` = فقط بعد از mount
- `[roomId]` = با تغییر roomId
- **همه reactive value های داخل effect باید در آرایه باشند** — افزونه‌ی lint خودش آن‌ها را اضافه می‌کند — دروغ گفتن به وابستگی‌ها یعنی باگ‌های عجیب

### تله‌های معروف ⭐

**۱) آبجکت/تابع به عنوان وابستگی:**
```tsx
useEffect(() => { ... }, [options]);   // ❌ options آبجکت جدید در هر رندر = بی‌نهایت اجرا
```
علاج: وابستگی‌های اتمی (`[options.host, options.port]`) یا useMemo.

**۲) race condition در fetch:**
```tsx
useEffect(() => {
  let ignore = false;
  fetch(`/api?q=${query}`)
    .then((r) => r.json())
    .then((d) => { if (!ignore) setResult(d); });
  return () => { ignore = true; };   // پاسخ دیرهنگام قبلی نادیده گرفته می‌شود
}, [query]);
```

**۳) Effects که لازم نیستند** — از داکیومنت «You Might Not Need an Effect»:
- state محاسبه‌شدنی → در رندر محاسبه کن
- واکنش به تغییر prop → در رندر (بدون state اضافی)
- event handling → در event handler، نه effect
- fetch داده → در اپ‌های جدی با فریم‌ورک (Next.js!) یا TanStack Query — نه useEffect خام

## ۳.۳ — Custom Hooks: منطق مشترک با قواعد React

تابعی که خودش از hook ها استفاده می‌کند — نامش با `use` شروع می‌شود:

```tsx
function useDebouncedValue<T>(value: T, delay = 300): T {
  const [debounced, setDebounced] = useState(value);

  useEffect(() => {
    const id = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(id);     // هر تغییر جدید، تایمر قبلی را لغو می‌کند
  }, [value, delay]);

  return debounced;
}

// مصرف:
const debouncedQuery = useDebouncedValue(query);
useEffect(() => { if (debouncedQuery) search(debouncedQuery); }, [debouncedQuery]);
```

Custom hook = **اشتراک منطق** (نه اشتراک state — هر فراخوانی، state مستقل خودش را دارد).

## ۳.۴ — Performance Hooks: useMemo و useCallback

```tsx
const filtered = useMemo(
  () => hugeList.filter((i) => i.active),
  [hugeList]
);

const handleSave = useCallback((id: number) => {
  save(id);
}, []);
```

| hook | چه چیزی را کش می‌کند | مصرفش وقتی؟ |
|---|---|---|
| `useMemo` | نتیجه محاسبه سنگین یا آبجکت پایدار برای وابستگی دیگری | محاسبه واقعاً سنگین یا مرجع ثابت لازم است |
| `useCallback` | خودِ تابع | پاس به کامپوننت memo شده یا وابستگی effect |

> ⚠️ داکیومنت React 19 لحنش این است: **به صورت پیش‌فرض استفاده نکن** — compiler آینده (React Compiler) خودش memo می‌کند؛ فقط جاهای واقعاً اندازه‌گیری‌شده اضافه کن. (مثل بهینه‌سازی کورکورانه دیتابیس — اول اندازه بگیر، بعد بهینه کن!)

## ۳.۵ — useSyncExternalStore (یک خط برای اشتراک store خارجی)

وقتی به store خارجی (نه state ری‌اکتی) وصل می‌شوی:

```tsx
const online = useSyncExternalStore(subscribe, () => navigator.onLine);
```

(عملاً پشت TanStack Query/Zustand است — شناختنش برای درک زیرساخت کافی است.)

---

## ✅ جمع‌بندی فصل

- ref = جعبه‌ی بی‌رندر (DOM + مقادیر فنی)؛ state را جایگزین نکن
- useEffect = همگام‌سازی بیرون؛ dependency ها صادقانه؛ cleanup همیشه
- fetch در effect = race با `ignore` — یا ابزار درست‌تر
- Custom hook = اشتراک منطق؛ naming با `use`
- useMemo/useCallback اندازه‌گیری‌شده، نه همه‌جا

## 📝 تمرین فصل ۳

1. این کد چه باگی دارد؟
```tsx
const [timer, setTimer] = useState<number>();
useEffect(() => {
  const id = setInterval(tick, 1000);
  setTimer(id);
}, []);
```
2. جستجوی زنده را با fetch در useEffect نوشتی و کاربر سریع تایپ می‌کند — دو مشکل پیش می‌آید؟ علاج هرکدام چیست؟
3. کدام را با ref و کدام را با state نگه می‌داری؟ (الف) مقدار toggle تم (ب) id تایمر (ج) مقدار input جستجو (د) آخرین scrollY
4. چرا `useEffect(() => {...}, [options])` با آبجکت options مشکل دارد و سه علاجش؟

<details><summary>جواب‌ها</summary>

1. تایمر هرگز clear نمی‌شود (لغو subscribe) — cleanup بنویس: `return () => clearInterval(id);` و لازم نیست تایمر state باشد — ref کافی است.
2. (۱) race condition — پاسخ دیرتر ممکن است قدیمی‌تر باشد → `ignore` flag یا AbortController؛ (۲) درخواست برای هر کلید! → debounce با custom hook.
3. state: (الف) و (ج)؛ ref: (ب) و (د).
4. آبجکت در هر رندر مرجع جدید دارد → effect بی‌نهایت اجرا می‌شود. علاج‌ها: وابستگی اتمی به فیلدهایش، useMemo برای پایدارسازی، یا تعریف آبجکت بیرون کامپوننت.
</details>

➡️ **فصل بعد:** React 19 و پترن‌های مدرن — use، useActionState، useOptimistic.
