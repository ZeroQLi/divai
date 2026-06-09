import { useRouter } from 'next/router';

export default function LangToggle() {
  const router = useRouter();
  const { locale, asPath } = router;
  const otherLocale = locale === 'en' ? 'ar' : 'en';

  return (
    <button
      type="button"
      onClick={() => router.push(asPath, asPath, { locale: otherLocale })}
    >
      {otherLocale === 'ar' ? 'العربية' : 'English'}
    </button>
  );
}
