// authSlice.js
import { createSlice } from '@reduxjs/toolkit';


const initialState = {
  isAuthenticated: false,
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
      state.isAuthenticated = action.payload;
      console.log(state.isAuthenticated);
      state.isAuthenticated = true;
      localStorage.setItem('authState', JSON.stringify(state));
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
