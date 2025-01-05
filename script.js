document.addEventListener('DOMContentLoaded', () => {
    const animationContainers = document.querySelectorAll('.animation-container');
  
    const handleScroll = () => {
      animationContainers.forEach((container) => {
        const rect = container.getBoundingClientRect();
        const windowHeight = window.innerHeight;
  
        // 當元素進入視窗範圍時觸發
        if (rect.top <= windowHeight * 0.6 && rect.bottom >= windowHeight * 0.4) {
          container.classList.add('active');
        }
      });
    };
  
    // 初始化滾動監聽
    window.addEventListener('scroll', handleScroll);
  });
  