import { apiSlice } from "../api";

const authSlice = apiSlice.injectEndpoints({
  overrideExisting: true,
  endpoints: (builder) => ({
    register: builder.mutation({
      query: (body) => ({
        url: "/signup",
        method: "POST",
        body,
      }),
    }),
    verifyEmail: builder.mutation({
      query: (body) => ({
        url: "/verify-email",
        method: "POST",
        body,
      }),
    }),

    resendCode: builder.mutation({
      query: (body) => ({
        url: "/resend-code",
        method: "POST",
        body,
      }),
    }),
    login: builder.mutation({
      query: (body) => ({
        url: "/login",
        method: "POST",
        body,
      }),
    }),
  }),
  // override:{
  //   fetchBaseQuery: (baseQuery) =>  {
  //    return (args)=> {
  //     return baseQuery({...args, credentials: "include"})
  //    }
    
  //   }
  // }
});

export const { useRegisterMutation, useVerifyEmailMutation, useResendCodeMutation, useLoginMutation } = authSlice;
