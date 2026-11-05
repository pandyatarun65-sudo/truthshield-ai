import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./AuthContext";
import Layout from "./components/Layout";
import AdminLayout from "./components/AdminLayout";
import Spinner from "./components/Spinner";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Home from "./pages/Home";
import Feed from "./pages/Feed";
import CreatePost from "./pages/CreatePost";
import PostDetail from "./pages/PostDetail";
import Profile from "./pages/Profile";
import Notifications from "./pages/Notifications";
import MyReports from "./pages/MyReports";
import AdminDashboard from "./pages/admin/Dashboard";
import AdminUsers from "./pages/admin/Users";
import AdminPosts from "./pages/admin/Posts";
import AdminReports from "./pages/admin/Reports";
import AdminKnowledge from "./pages/admin/Knowledge";
import AdminAnalytics from "./pages/admin/Analytics";
import AdminLogs from "./pages/admin/Logs";

function Protected({ children, staff }) {
  const { user, loading } = useAuth();
  if (loading) return <Spinner label="Loading..." />;
  if (!user) return <Navigate to="/login" replace />;
  if (staff && !["admin", "moderator"].includes(user.role)) return <Navigate to="/feed" replace />;
  return children;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route element={<Protected><Layout /></Protected>}>
        <Route path="/" element={<Home />} />
        <Route path="/feed" element={<Feed />} />
        <Route path="/explore" element={<Feed explore />} />
        <Route path="/create-post" element={<CreatePost />} />
        <Route path="/post/:id" element={<PostDetail />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/notifications" element={<Notifications />} />
        <Route path="/reports" element={<MyReports />} />
      </Route>
      <Route path="/admin" element={<Protected staff><AdminLayout /></Protected>}>
        <Route index element={<AdminDashboard />} />
        <Route path="users" element={<AdminUsers />} />
        <Route path="posts" element={<AdminPosts />} />
        <Route path="reports" element={<AdminReports />} />
        <Route path="knowledge-base" element={<AdminKnowledge />} />
        <Route path="analytics" element={<AdminAnalytics />} />
        <Route path="logs" element={<AdminLogs />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
