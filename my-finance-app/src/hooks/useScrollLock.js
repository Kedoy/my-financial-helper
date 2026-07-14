import { useRef, useLayoutEffect } from 'react';

export function useScrollLock(dependencies) {
  const scrollRef = useRef(0);
  
  const savePosition = () => {
    scrollRef.current = window.scrollY;
  };
  
  useLayoutEffect(() => {
    const id = requestAnimationFrame(() => {
      window.scrollTo(0, scrollRef.current);
    });
    return () => cancelAnimationFrame(id);
  }, dependencies);
  
  return savePosition;
}
