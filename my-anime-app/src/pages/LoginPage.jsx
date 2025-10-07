import { useState, useContext } from "react";
import { useNavigate, Link } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import { motion } from "framer-motion";

const LoginPage = () => {
  const navigate = useNavigate();
  const { loginUser } = useContext(AuthContext);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    const success = await loginUser(username, password);
    success ? navigate("/") : setError("Неверный логин или пароль");
  };

  return (
    <div className="min-h-screen flex justify-center items-center bg-gradient-to-br from-[#0f172a] via-[#1e293b] to-[#0f172a] text-white">
      <motion.form
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        onSubmit={handleSubmit}
        className="bg-black/50 backdrop-blur-lg p-10 rounded-2xl w-96 border border-white/10 shadow-2xl space-y-6"
      >
        <h2 className="text-3xl font-bold text-center text-blue-400 tracking-wide">
          Войти в AnimeFinder
        </h2>

        {error && <p className="text-red-400 text-center">{error}</p>}

        <div className="space-y-4">
          <input
            type="text"
            placeholder="Имя пользователя"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full p-3 rounded-lg bg-gray-800/70 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
            required
          />
          <input
            type="password"
            placeholder="Пароль"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full p-3 rounded-lg bg-gray-800/70 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
            required
          />
        </div>

        <button
          type="submit"
          className="w-full bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white font-semibold py-3 rounded-lg shadow-lg transition-transform hover:scale-[1.02]"
        >
          Войти
        </button>

        <p className="text-center text-gray-400 text-sm mt-4">
          Нет аккаунта?{" "}
          <Link to="/register" className="text-blue-400 hover:text-blue-300 underline">
            Зарегистрироваться
          </Link>
        </p>
      </motion.form>
    </div>
  );
};

export default LoginPage;
