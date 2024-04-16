import { apiSlice } from "../api";
import Cookies from "js-cookie";
const taskSlice = apiSlice.injectEndpoints({
  overrideExisting: true,
  endpoints: (builder) => ({
    getProducts: builder.query({
      query: () => ({
        url: "/items",
        method: "GET",
        headers: {
          "X-CSRF-TOKEN": Cookies.get("csrf_access_token"),
        },
      }),
    }),
    getSingleProduct: builder.query({
      query: (id) => ({
        url: `/items/${id}`,
        method: "GET",
        headers: {
          "X-CSRF-TOKEN": Cookies.get("csrf_access_token"),
        },
      }),
    }),
    newProduct: builder.mutation({
      query: () => ({
        url: "/items/new",
        method: "POST",
        headers: {
          "X-CSRF-TOKEN": Cookies.get("csrf_access_token"),
        },
      }),
    }),
    updateProduct: builder.mutation({
      query: (id) => ({
        url: `/items/update/${id}`,
        method: "PUT",
        headers: {
          "X-CSRF-TOKEN": Cookies.get("csrf_access_token"),
        },
      }),
    }),
    deleteProduct: builder.mutation({
      query: (id) => ({
        url: `/items/delete/${id}`,
        method: "DELETE",
        headers: {
          "X-CSRF-TOKEN": Cookies.get("csrf_access_token"),
        },
      }),
    }),

  }),
});

export const {
    useGetProductsQuery,
    useGetSingleProductQuery,
    useNewProductMutation,
    useUpdateProductMutation,
    useDeleteProductMutation,
} = taskSlice;
