import { Component, type ErrorInfo, type ReactNode } from "react";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
}

export default class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    // eslint-disable-next-line no-console
    console.error("Unhandled error caught by ErrorBoundary:", error, info);
  }

  handleReload = () => {
    this.setState({ hasError: false });
    window.location.assign("/");
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-main px-4 text-center">
          <h1 className="font-display text-2xl font-medium text-heading">
            Something went wrong.
          </h1>
          <p className="max-w-md text-sm leading-6 text-secondary">
            An unexpected error occurred. You can try reloading the page —
            if the problem continues, please reach out to support.
          </p>
          <button type="button" onClick={this.handleReload} className="beauty-button px-7">
            Reload page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
