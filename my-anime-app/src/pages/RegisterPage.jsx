import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/axios";
import { motion } from "framer-motion";

const RegisterPage = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await api.post("/reg/register", { username, email, password });
      navigate("/check-email");
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(Array.isArray(detail) ? detail.map((d) => d.msg).join(", ") : detail || "Ошибка регистрации.");
    }
  };

  return (
    <div className="min-h-screen flex justify-center items-center bg-gradient-to-br from-[#0f172a] via-[#1e293b] to-[#0f172a] text-white">
      <motion.form
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        onSubmit={handleSubmit}
        className="bg-black/50 backdrop-blur-lg p-10 rounded-2xl w-96 border border-white/10 shadow-2xl space-y-6"
      >
        <h2 className="text-3xl font-bold text-center text-green-400 tracking-wide">
          Регистрация в AnimeFinder
        </h2>

        {error && <p className="text-red-400 text-center">{error}</p>}

        <div className="space-y-4">
          <input
            type="text"
            placeholder="Имя пользователя"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full p-3 rounded-lg bg-gray-800/70 text-white focus:outline-none focus:ring-2 focus:ring-green-500 transition"
            required
          />
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full p-3 rounded-lg bg-gray-800/70 text-white focus:outline-none focus:ring-2 focus:ring-green-500 transition"
            required
          />
          <input
            type="password"
            placeholder="Пароль"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full p-3 rounded-lg bg-gray-800/70 text-white focus:outline-none focus:ring-2 focus:ring-green-500 transition"
            required
          />
        </div>

        <button
          type="submit"
          className="w-full bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white font-semibold py-3 rounded-lg shadow-lg transition-transform hover:scale-[1.02]"
        >
          Зарегистрироваться
        </button>
      </motion.form>
    </div>
  );
};

export default RegisterPage;
