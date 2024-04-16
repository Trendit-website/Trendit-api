import { apiSlice } from "../api";
import Cookies from 'js-cookie';
const taskSlice = apiSlice.injectEndpoints({
  overrideExisting: true,
  endpoints: (builder) => ({
    getTasks: builder.query({
      query: () => ({
        url: "/tasks",
        method: "GET",
        headers: {
          'X-CSRF-TOKEN': Cookies.get('csrf_access_token'),
        },
  
      }),
    }),
    getAdvertTasks: builder.query({
      query: () => ({
        url: "/tasks/advert",
        method: "GET",
        headers: {
          'X-CSRF-TOKEN': Cookies.get('csrf_access_token'),
        },
  
      }),
    }),
    getEngagementTasks: builder.query({
      query: () => ({
        url: "/tasks/engagement",
        method: "GET",
        headers: {
          'X-CSRF-TOKEN': Cookies.get('csrf_access_token'),
        },
  
      }),
    }),
  }),
});

export const {useGetTasksQuery, useGetAdvertTasksQuery, useGetEngagementTasksQuery} = taskSlice;
