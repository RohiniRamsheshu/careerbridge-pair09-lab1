import { configureStore } from "@reduxjs/toolkit";
import { assistantReducer, applicationsReducer, authReducer, eventsReducer, jobsReducer, savedReducer } from "./slices.js";

export const store = configureStore({ reducer: { auth: authReducer, jobs: jobsReducer, applications: applicationsReducer, events: eventsReducer, saved: savedReducer, assistant: assistantReducer }, devTools: import.meta.env?.DEV ?? true });
