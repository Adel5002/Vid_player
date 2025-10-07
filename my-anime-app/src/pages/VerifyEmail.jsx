import { useSearchParams } from "react-router-dom";

export default function VerifyEmail() {
  const [searchParams] = useSearchParams();
  const status = searchParams.get("status");
  const reason = searchParams.get("reason");

  let message = "";
  if (status === "success") {
    message = "Теперь вы можете войти в свой аккаунт.";
  } else {
    switch (reason) {
      case "invalid_token":
        message = "Некорректная ссылка подтверждения.";
        break;
      case "user_not_found":
        message = "Пользователь не найден.";
        break;
      case "expired_or_used":
        message = "Эта ссылка уже была использована или устарела.";
        break;
      default:
        message = "Ссылка недействительна или устарела.";
    }
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-b from-[#0a0f1f] via-[#121a2b] to-[#0a0f1f] text-white px-4">
      {status === "success" ? (
        <div className="text-center bg-green-600/10 border border-green-400/30 rounded-2xl p-8 max-w-md">
          <h1 className="text-3xl font-bold text-green-400 mb-3">✅ Email подтверждён!</h1>
          <p className="text-gray-300 mb-4">{message}</p>
          <a href="/login" className="text-blue-400 hover:underline">
            Перейти к входу
          </a>
        </div>
      ) : (
        <div className="text-center bg-red-600/10 border border-red-400/30 rounded-2xl p-8 max-w-md">
          <h1 className="text-3xl font-bold text-red-400 mb-3">❌ Ошибка</h1>
          <p className="text-gray-300 mb-4">{message}</p>
          <a href="/register" className="text-blue-400 hover:underline">
            Зарегистрироваться снова
          </a>
        </div>
      )}
    </div>
  );
}
