import { Component } from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("ErrorBoundary caught:", error, errorInfo);
  }

  handleRefresh = () => {
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-[#050505] flex items-center justify-center px-4" data-testid="error-boundary">
          <div className="text-center max-w-md">
            <div className="w-16 h-16 rounded-full bg-red-500/10 flex items-center justify-center mx-auto mb-6">
              <AlertTriangle className="w-8 h-8 text-red-400" />
            </div>
            <h1 className="text-2xl font-bold font-['Outfit'] text-white mb-3" data-testid="error-boundary-title">
              Something went wrong
            </h1>
            <p className="text-zinc-500 text-sm mb-6">
              Something went wrong. Please refresh.
            </p>
            <button
              onClick={this.handleRefresh}
              className="inline-flex items-center gap-2 px-6 py-3 bg-[#7B61FF] hover:bg-[#7B61FF]/90 text-white text-sm font-medium rounded-full transition-colors"
              data-testid="error-boundary-refresh-btn"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh Page
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
