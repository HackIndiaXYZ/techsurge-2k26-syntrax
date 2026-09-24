import { NextResponse } from 'next/server';
import { createServerClient } from '@supabase/ssr';
import { cookies } from 'next/headers';

export async function GET(request: Request) {
  const requestUrl = new URL(request.url);
  const code = requestUrl.searchParams.get('code');
  const token_hash = requestUrl.searchParams.get('token_hash');
  const type = requestUrl.searchParams.get('type');
  const next = requestUrl.searchParams.get('next') ?? '/dashboard';
  const error_description = requestUrl.searchParams.get('error_description');
  
  if (error_description) {
    return NextResponse.redirect(`${requestUrl.origin}/login?error=${encodeURIComponent(error_description)}`);
  }

  if (code || (token_hash && type)) {
    const cookieStore = await cookies();
    const supabase = createServerClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
      {
        cookies: {
          getAll() {
            return cookieStore.getAll();
          },
          setAll(cookiesToSet) {
            cookiesToSet.forEach(({ name, value, options }) =>
              cookieStore.set(name, value, options)
            );
          },
        },
      }
    );
    
    let error = null;
    
    if (code) {
      const { error: codeError } = await supabase.auth.exchangeCodeForSession(code);
      error = codeError;
    } else if (token_hash && type) {
      const { error: otpError } = await supabase.auth.verifyOtp({
        token_hash,
        type: type as any,
      });
      error = otpError;
    }
    
    if (!error) {
      return NextResponse.redirect(`${requestUrl.origin}${next}`);
    } else {
      console.error('Error in auth callback:', error);
      if (error.message && error.message.includes('PKCE code verifier not found')) {
        // The email was confirmed by the Supabase API, but we couldn't automatically log them in
        // because they clicked the link in a different browser/device.
        // That's fine, we just redirect them to login manually.
        return NextResponse.redirect(`${requestUrl.origin}/login?message=Email+confirmed+successfully!+Please+log+in+to+continue.`);
      }
      return NextResponse.redirect(`${requestUrl.origin}/login?error=${encodeURIComponent(error.message)}`);
    }
  }

  // URL to redirect to after sign in process completes
  return NextResponse.redirect(`${requestUrl.origin}/login?error=Invalid+or+expired+confirmation+link`);
}
