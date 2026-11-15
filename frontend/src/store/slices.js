import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import * as api from "../services/api.js";

const requestState = { status: "idle", error: null };

export const restoreSession = createAsyncThunk("auth/restore", async () => {
  const user = await api.getMe();
  if (!api.isAuthenticatedUser(user)) throw new Error("Invalid session response.");
  return user;
});
export const loginSession = createAsyncThunk("auth/login", ({ email, password }) => api.login(email, password));
const authSlice = createSlice({ name: "auth", initialState: { user: null, ...requestState }, reducers: { sessionSet(state, action) { state.user = action.payload; state.status = "succeeded"; state.error = null; }, loggedOut(state) { state.user = null; state.status = "idle"; state.error = null; } }, extraReducers: (builder) => builder
  .addCase(restoreSession.pending, (state) => { state.status = "loading"; })
  .addCase(restoreSession.fulfilled, (state, action) => { state.user = action.payload; state.status = "succeeded"; })
  .addCase(restoreSession.rejected, (state, action) => { state.status = "failed"; state.error = action.error.message; })
  .addCase(loginSession.pending, (state) => { state.status = "loading"; state.error = null; })
  .addCase(loginSession.fulfilled, (state, action) => { state.user = action.payload.user; state.status = "succeeded"; })
  .addCase(loginSession.rejected, (state, action) => { state.status = "failed"; state.error = action.error.message; }) });

export const loadJobs = createAsyncThunk("jobs/load", (filters) => api.getJobs(filters));
const jobsSlice = createSlice({ name: "jobs", initialState: { items: [], total: 0, limit: 50, offset: 0, filters: {}, ...requestState }, reducers: { filtersChanged(state, action) { state.filters = action.payload; } }, extraReducers: (builder) => builder.addCase(loadJobs.pending, (state) => { state.status = "loading"; }).addCase(loadJobs.fulfilled, (state, action) => { const payload = action.payload; state.items = Array.isArray(payload) ? payload : (Array.isArray(payload?.items) ? payload.items : []); state.total = Array.isArray(payload) ? state.items.length : (payload.total ?? 0); state.limit = Array.isArray(payload) ? state.limit : (payload.limit ?? state.limit); state.offset = Array.isArray(payload) ? state.offset : (payload.offset ?? state.offset); state.status = "succeeded"; }).addCase(loadJobs.rejected, (state, action) => { state.status = "failed"; state.error = action.error.message; }) });

export const loadApplications = createAsyncThunk("applications/load", () => api.getStudentApplications());
const applicationsSlice = createSlice({ name: "applications", initialState: { items: [], selectedStatus: "All", ...requestState }, reducers: { statusFilterChanged(state, action) { state.selectedStatus = action.payload; }, applicationUpdated(state, action) { const index = state.items.findIndex((item) => item.id === action.payload.id); if (index >= 0) state.items[index] = { ...state.items[index], ...action.payload }; } }, extraReducers: (builder) => builder.addCase(loadApplications.pending, (state) => { state.status = "loading"; }).addCase(loadApplications.fulfilled, (state, action) => { state.items = Array.isArray(action.payload) ? action.payload : []; state.status = "succeeded"; }).addCase(loadApplications.rejected, (state, action) => { state.status = "failed"; state.error = action.error.message; }) });

export const loadEvents = createAsyncThunk("events/load", (filters) => api.getEvents(filters));
const eventsSlice = createSlice({ name: "events", initialState: { items: [], total: 0, limit: 50, offset: 0, registrations: [], ...requestState }, reducers: { registrationAdded(state, action) { state.registrations.push(action.payload); } }, extraReducers: (builder) => builder.addCase(loadEvents.pending, (state) => { state.status = "loading"; }).addCase(loadEvents.fulfilled, (state, action) => { const payload = action.payload; state.items = Array.isArray(payload) ? payload : (Array.isArray(payload?.items) ? payload.items : []); state.total = Array.isArray(payload) ? state.items.length : (payload.total ?? 0); state.limit = Array.isArray(payload) ? state.limit : (payload.limit ?? state.limit); state.offset = Array.isArray(payload) ? state.offset : (payload.offset ?? state.offset); state.status = "succeeded"; }).addCase(loadEvents.rejected, (state, action) => { state.status = "failed"; state.error = action.error.message; }) });

export const loadSavedItems = createAsyncThunk("saved/load", () => api.getSavedItems());
const savedSlice = createSlice({ name: "saved", initialState: { items: [], ...requestState }, reducers: { itemAdded(state, action) { state.items.push(action.payload); }, itemRemoved(state, action) { state.items = state.items.filter((item) => item.id !== action.payload); } }, extraReducers: (builder) => builder.addCase(loadSavedItems.pending, (state) => { state.status = "loading"; }).addCase(loadSavedItems.fulfilled, (state, action) => { state.items = Array.isArray(action.payload) ? action.payload : []; state.status = "succeeded"; }).addCase(loadSavedItems.rejected, (state, action) => { state.status = "failed"; state.error = action.error.message; }) });

export const sendAssistantMessage = createAsyncThunk("assistant/send", ({ message, conversationId }) => api.assistantChat(message, conversationId));
function assistantDisplay(answer) { return typeof answer === "string" && /^\s*(get_student_preferences|search_jobs|get_job_details|search_events|save_job_or_event)\s*\(/i.test(answer) ? "I couldn't complete that request safely. Please try again." : answer; }
function pendingFromAnswer(answer) { const match = typeof answer === "string" && answer.match(/Confirmation required:\s*(\{.*\})/s); if (!match) return null; try { return JSON.parse(match[1]); } catch { return null; } }
const assistantSlice = createSlice({ name: "assistant", initialState: { conversationId: null, messages: [{ sender: "assistant", text: "Hi! I can help you find jobs and events in the Pair 09 region." }], pendingSave: null, metrics: null, ...requestState }, reducers: { conversationStarted(state, action) { state.conversationId = action.payload || null; state.messages = [{ sender: "assistant", text: "Hi! I can help you find jobs and events in the Pair 09 region." }]; state.pendingSave = null; state.metrics = null; state.error = null; }, messageAdded(state, action) { state.messages.push(action.payload); }, confirmationResolved(state, action) { state.pendingSave = null; state.messages.push(action.payload); } }, extraReducers: (builder) => builder.addCase(sendAssistantMessage.pending, (state, action) => { state.status = "loading"; state.error = null; state.messages.push({ sender: "user", text: action.meta.arg.message }); }).addCase(sendAssistantMessage.fulfilled, (state, action) => { state.status = "succeeded"; state.conversationId = action.payload.conversation_id; state.messages.push({ sender: "assistant", text: assistantDisplay(action.payload.answer) }); state.pendingSave = pendingFromAnswer(action.payload.answer); state.metrics = action.payload.metrics || null; }).addCase(sendAssistantMessage.rejected, (state, action) => { state.status = "failed"; state.error = action.error.message; }) });

export const { sessionSet, loggedOut } = authSlice.actions;
export const { filtersChanged } = jobsSlice.actions;
export const { statusFilterChanged, applicationUpdated } = applicationsSlice.actions;
export const { registrationAdded } = eventsSlice.actions;
export const { itemAdded, itemRemoved } = savedSlice.actions;
export const { conversationStarted, messageAdded, confirmationResolved } = assistantSlice.actions;
export const authReducer = authSlice.reducer;
export const jobsReducer = jobsSlice.reducer;
export const applicationsReducer = applicationsSlice.reducer;
export const eventsReducer = eventsSlice.reducer;
export const savedReducer = savedSlice.reducer;
export const assistantReducer = assistantSlice.reducer;

export const selectUser = (state) => state.auth.user;
export const selectJobs = (state) => state.jobs.items;
export const selectApplications = (state) => state.applications.items;
export const selectEvents = (state) => state.events.items;
export const selectSavedItems = (state) => state.saved.items;
export const selectAssistant = (state) => state.assistant;
