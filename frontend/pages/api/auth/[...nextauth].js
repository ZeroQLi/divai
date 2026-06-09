import NextAuth from 'next-auth';

export default NextAuth({
  providers: [
    {
      id: 'uae-pass',
      name: 'UAE PASS',
      type: 'oauth',
      version: '2.0',
      authorization: {
        url: 'https://stg-id.uaepass.ae/idshub/authorize',
        params: {
          scope: 'urn:uae:digitalid:profile:general',
          acr_values: 'urn:safelayer:tws:policies:authentication:level:low',
        },
      },
      token: 'https://stg-id.uaepass.ae/idshub/token',
      userinfo: 'https://stg-id.uaepass.ae/idshub/userinfo',
      clientId: process.env.UAEPASS_CLIENT_ID,
      clientSecret: process.env.UAEPASS_CLIENT_SECRET,
      checks: ['pkce', 'state'],
      profile(profile) {
        return {
          id: profile.sub,
          name: profile.fullnameEN,
          email: profile.email,
          image: profile.image || null,
          fullnameEN: profile.fullnameEN,
          fullnameAR: profile.fullnameAR,
          gender: profile.gender,
        };
      },
    },
  ],
  session: { strategy: 'jwt' },
  callbacks: {
    async jwt({ token, account, profile }) {
      if (account) {
        token.provider = account.provider;
      }
      if (profile) {
        token.profile = profile;
      }
      return token;
    },
    async session({ session, token }) {
      session.user.id = token.sub;
      session.user.provider = token.provider;
      session.profile = token.profile;
      return session;
    },
  },
});
