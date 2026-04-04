import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Home, ArrowLeft } from "lucide-react";
import { Button } from "../components/ui/button";

const NotFoundPage = () => {
  return (
    <div className="min-h-screen flex items-center justify-center px-4" data-testid="not-found-page">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center max-w-md"
      >
        <div className="text-8xl font-bold font-['Outfit'] bg-gradient-to-r from-[#7B61FF] to-[#00FF94] bg-clip-text text-transparent mb-4">
          404
        </div>
        <h1 className="text-2xl font-bold mb-2" data-testid="not-found-title">Page Not Found</h1>
        <p className="text-zinc-500 mb-8">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <div className="flex items-center justify-center gap-3">
          <Button asChild variant="outline" className="rounded-full border-zinc-700 hover:border-zinc-500">
            <Link to="/" data-testid="not-found-home-btn">
              <Home className="w-4 h-4 mr-2" />Home
            </Link>
          </Button>
          <Button
            onClick={() => window.history.back()}
            className="rounded-full bg-[#7B61FF] hover:bg-[#7B61FF]/90"
            data-testid="not-found-back-btn"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />Go Back
          </Button>
        </div>
      </motion.div>
    </div>
  );
};

export default NotFoundPage;
