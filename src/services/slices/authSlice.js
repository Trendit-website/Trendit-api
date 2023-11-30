// authSlice.js
import { createSlice } from '@reduxjs/toolkit';


const initialState = {
  name: 'auth',
  isAuthenticated: false,
  user: null,
  auth: '',
  // Add other authentication-related state here
};
const loadStateFromLocalStorage = () => {
  try {
    const serializedState = localStorage.getItem('authState');
    if (serializedState === null) {
      return undefined;
    }
    return JSON.parse(serializedState);
  } catch (err) {
    return undefined;
  }
};

const saveStateToLocalStorage = (state) => {
  try {
    const { isAuthenticated, user } = state;
    const serializedState = JSON.stringify({ isAuthenticated, user });
    localStorage.setItem('authState', serializedState);
  } catch (err) {
    console.log(err);
    // Handle potential errors here
  }
};

const authSlice = createSlice({
  name: 'auth',
  initialState: loadStateFromLocalStorage() || initialState,
  reducers: {
    loginSuccess: (state, action) => {
      state.isAuthenticated = true;
      state.user = action.payload;
      saveStateToLocalStorage(state);
    },
    logout: (state) => {
      state.isAuthenticated = false;
      state.user = null;
      saveStateToLocalStorage(state);
    },
  },
});

export const { loginSuccess, logout } = authSlice.actions;
export default authSlice.reducer;
