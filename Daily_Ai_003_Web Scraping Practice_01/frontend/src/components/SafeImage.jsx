import { useState } from "react";

export default function SafeImage({
  src,
  alt,
  className = "",
  fallbackHref = "",
  fallbackAction = "開啟原文",
  ...props
}) {
  const [failed, setFailed] = useState(false);

  if (!src || failed) {
    return (
      <span className={`image-fallback ${className}`} title={fallbackHref || src}>
        <strong>圖片無法載入</strong>
        <span>{fallbackAction}</span>
      </span>
    );
  }

  return (
    <img
      className={className}
      src={src}
      alt={alt}
      loading="lazy"
      decoding="async"
      referrerPolicy="no-referrer"
      onError={() => setFailed(true)}
      {...props}
    />
  );
}
