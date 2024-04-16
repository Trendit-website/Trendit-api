import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'
import { config } from '../config'

const PROD = config.apiUrl

export const apiSlice = createApi({
    reducerPath: 'apiSlice',
    baseQuery: fetchBaseQuery({ baseUrl: PROD, credentials: "include"}),
    keepUnusedDataFor: 30,
    endpoints:() => ({})
})