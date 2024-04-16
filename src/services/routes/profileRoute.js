import { apiSlice } from "../api";
import Cookies from "js-cookie";
const taskSlice = apiSlice.injectEndpoints({
  overrideExisting: true,
  endpoints: (builder) => ({
    getProfile: builder.query({
      query: () => ({
        url: "/profile",
        method: "GET",
        headers: {
          "X-CSRF-TOKEN": Cookies.get("csrf_access_token"),
        },
      }),
    }),
    // getStates: builder.mutation({
    //   query: () => ({
    //     url: "/profile/edit",
    //     method: "POST",
    //     headers: {
    //       "X-CSRF-TOKEN": Cookies.get("csrf_access_token"),
    //     },
    //   }),
    // }),
    getProfilePic: builder.query({
      query: () => ({
        url: "/profile-pic",
        method: "GET",
        headers: {
          "X-CSRF-TOKEN": Cookies.get("csrf_access_token"),
        },
      }),
    }),
  }),
});

export const {
    useGetProfileQuery,
    // useGetStatesMutation,
    useGetProfilePicQuery,
} = taskSlice;
