import { apiSlice } from "../api";
import Cookies from 'js-cookie';
const taskSlice = apiSlice.injectEndpoints({
  overrideExisting: true,
  endpoints: (builder) => ({
    getCountries    : builder.query({
      query: () => ({
        url: "/countries",
        method: "GET",
        headers: {
          'X-CSRF-TOKEN': Cookies.get('csrf_access_token'),
        },
  
      }),
    }),
    getStates: builder.query({
        query: (country) => ({
            url: `/states?country=${country}`,
        method: "GET",
        headers: {
          'X-CSRF-TOKEN': Cookies.get('csrf_access_token'),
        },
  
      }),
    }),
    getLocals: builder.query({
      query: (lga) => ({
        url: `/states/lga/${lga}`,
        method: "GET",
        headers: {
          'X-CSRF-TOKEN': Cookies.get('csrf_access_token'),
        },
  
      }),
    }),
  }),
});

export const {
    useGetCountriesQuery,
    useLazyGetStatesQuery,
    useLazyGetLocalsQuery
} = taskSlice;
