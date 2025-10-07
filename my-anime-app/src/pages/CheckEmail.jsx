import { useEffect, useState } from "react";
import { motion } from "framer-motion";

export default function CheckEmailPage() {
  const [message, setMessage] = useState("");

  useEffect(() => {
    const msg = localStorage.getItem("checkEmailMessage");
    if (msg) {
      setMessage(msg);
      localStorage.removeItem("checkEmailMessage");
    }
  }, []);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#0f172a] via-[#1e293b] to-[#0f172a] text-white px-4">
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center bg-black/40 backdrop-blur-lg border border-white/10 rounded-2xl p-10 shadow-2xl"
      >
        <h1 className="text-3xl font-bold mb-4 text-blue-400">📩 Проверьте почту</h1>
        <p className="text-gray-300 text-lg">
          {message || "Мы отправили вам письмо для подтверждения аккаунта."}
        </p>
      </motion.div>
    </div>
  );
}
