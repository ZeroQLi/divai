import { getSession, signIn } from 'next-auth/react';
import { useRouter } from 'next/router';
import { useEffect } from 'react';
import LangToggle from '../components/LangToggle';
import en from '../locales/en.json';
import ar from '../locales/ar.json';

export default function Login() {
  const router = useRouter();
  const t = router.locale === 'ar' ? ar : en;

  useEffect(() => {
    getSession().then(session => {
      if (session) router.replace('/');
    });
  }, [router]);

  return (
    <div style={{ maxWidth: 420, margin: '5vh auto', textAlign: 'center' }}>
      <LangToggle />
      <h1>{t['app.title']}</h1>
      <h2>{t['login.title']}</h2>
      <button onClick={() => signIn('uae-pass')}>{t['login.uaepass']}</button>
    </div>
  );
}
