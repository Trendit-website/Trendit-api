import React from "react";
import { useNavigate } from "react-router-dom";

const Result = () => {
  const navigate = useNavigate();
  const goBack = () => {
    navigate("/dashboard");
  };
  const goDetails = () => {
    navigate("/task_detail");
  };
  return (
    <body className="bg-[#000] min-h-[100svh]">
      <div>
        <div className="bg-[#121212] w-full fixed items-center mb-[40px] flex justify-between py-[16.31px] px-[16.07px] md:hidden">
          <div
            onClick={goBack}
            className="text-[#fff] tracking-[0.169px] font-[500] clashmd text-[16.921px]"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="15"
              height="12"
              viewBox="0 0 15 12"
              fill="none"
            >
              <path
                d="M5.808 1.16354C5.99134 1.34688 6.07934 1.5684 6.072 1.82813C6.06467 2.08785 5.96903 2.30937 5.78509 2.49271L3.1955 5.08229L13.4163 5.08229C13.6761 5.08229 13.8939 5.17029 14.0699 5.34629C14.2459 5.52229 14.3336 5.73985 14.333 5.99896C14.333 6.25868 14.245 6.47654 14.069 6.65254C13.893 6.82854 13.6754 6.91624 13.4163 6.91563L3.1955 6.91563L5.808 9.52813C5.99134 9.71146 6.083 9.92932 6.083 10.1817C6.083 10.4341 5.99134 10.6517 5.808 10.8344C5.62467 11.0177 5.40681 11.1094 5.15442 11.1094C4.90203 11.1094 4.68448 11.0177 4.50175 10.8344L0.308004 6.64062C0.216338 6.54896 0.151254 6.44965 0.112754 6.34271C0.074254 6.23576 0.0553093 6.12118 0.0559196 5.99896C0.0559196 5.87674 0.0751715 5.76215 0.113671 5.65521C0.152171 5.54826 0.216949 5.44896 0.308004 5.35729L4.52467 1.14063C4.69273 0.97257 4.90264 0.888541 5.15442 0.888541C5.4062 0.888541 5.62406 0.980208 5.808 1.16354Z"
                fill="white"
              />
            </svg>
          </div>
          <div className="flex items-center space-x-[16px]">
            <div>
              <img src="/img/notismall.svg" className="cursor-pointer" />
            </div>
            <div className="cursor-pointer">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="30"
                height="30"
                viewBox="0 0 30 30"
                fill="none"
              >
                <path
                  d="M5 22.5H25C25.6875 22.5 26.25 21.9375 26.25 21.25C26.25 20.5625 25.6875 20 25 20H5C4.3125 20 3.75 20.5625 3.75 21.25C3.75 21.9375 4.3125 22.5 5 22.5ZM5 16.25H25C25.6875 16.25 26.25 15.6875 26.25 15C26.25 14.3125 25.6875 13.75 25 13.75H5C4.3125 13.75 3.75 14.3125 3.75 15C3.75 15.6875 4.3125 16.25 5 16.25ZM3.75 8.75C3.75 9.4375 4.3125 10 5 10H25C25.6875 10 26.25 9.4375 26.25 8.75C26.25 8.0625 25.6875 7.5 25 7.5H5C4.3125 7.5 3.75 8.0625 3.75 8.75Z"
                  fill="white"
                />
              </svg>
            </div>
          </div>
        </div>
        <div className="hidden bg-[#000] fixed items-center justify-between border-b border-[#333] md:flex w-full px-[30px] py-[28px]">
          <div onClick={goBack} className="cursor-pointer">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
            >
              <path
                d="M10.875 19.3015L4.27502 12.7015C4.17502 12.6015 4.10402 12.4932 4.06202 12.3765C4.02002 12.2599 3.99935 12.1349 4.00002 12.0015C4.00002 11.8682 4.02102 11.7432 4.06302 11.6265C4.10502 11.5099 4.17568 11.4015 4.27502 11.3015L10.875 4.70153C11.0583 4.51819 11.2877 4.42253 11.563 4.41453C11.8383 4.40653 12.0757 4.50219 12.275 4.70153C12.475 4.88486 12.5793 5.11419 12.588 5.38953C12.5967 5.66486 12.5007 5.90219 12.3 6.10153L7.40002 11.0015H18.575C18.8583 11.0015 19.096 11.0975 19.288 11.2895C19.48 11.4815 19.5757 11.7189 19.575 12.0015C19.575 12.2849 19.4793 12.5225 19.288 12.7145C19.0967 12.9065 18.859 13.0022 18.575 13.0015H7.40002L12.3 17.9015C12.4833 18.0849 12.5793 18.3182 12.588 18.6015C12.5967 18.8849 12.5007 19.1182 12.3 19.3015C12.1167 19.5015 11.8833 19.6015 11.6 19.6015C11.3167 19.6015 11.075 19.5015 10.875 19.3015Z"
                fill="white"
              />
            </svg>
          </div>
          <div className="flex items-center space-x-[20px]">
            <div className="rounded-[8px] cursor-pointer w-fit p-[9px] bg-[#333]">
              <div className="relative z-[10] ml-[9px]">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="9"
                  height="10"
                  viewBox="0 0 9 10"
                  fill="none"
                >
                  <circle cx="4.5" cy="4.60156" r="4.5" fill="#F13A5B" />
                </svg>
              </div>
              <div className="mx-auto relative mt-[-10px]">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="21"
                  height="21"
                  viewBox="0 0 21 21"
                  fill="none"
                >
                  <path
                    d="M14.0253 18.3984C14.0253 18.5642 13.9595 18.7232 13.8423 18.8404C13.7251 18.9576 13.5661 19.0234 13.4003 19.0234H8.40034C8.23458 19.0234 8.07561 18.9576 7.9584 18.8404C7.84119 18.7232 7.77534 18.5642 7.77534 18.3984C7.77534 18.2327 7.84119 18.0737 7.9584 17.9565C8.07561 17.8393 8.23458 17.7734 8.40034 17.7734H13.4003C13.5661 17.7734 13.7251 17.8393 13.8423 17.9565C13.9595 18.0737 14.0253 18.2327 14.0253 18.3984ZM18.2292 14.6438C17.7949 13.8969 17.1503 11.7836 17.1503 9.02344C17.1503 7.36583 16.4919 5.77612 15.3198 4.60402C14.1477 3.43192 12.5579 2.77344 10.9003 2.77344C9.24274 2.77344 7.65302 3.43192 6.48092 4.60402C5.30882 5.77612 4.65034 7.36583 4.65034 9.02344C4.65034 11.7844 4.00503 13.8969 3.57143 14.6438C3.46071 14.8336 3.40201 15.0493 3.40125 15.2691C3.4005 15.4889 3.45772 15.7051 3.56714 15.8957C3.67656 16.0863 3.83431 16.2447 4.02448 16.355C4.21466 16.4652 4.43054 16.5233 4.65034 16.5234H17.1503C17.3701 16.5231 17.5859 16.4649 17.7759 16.3547C17.966 16.2444 18.1236 16.086 18.233 15.8954C18.3423 15.7047 18.3994 15.4887 18.3986 15.269C18.3979 15.0492 18.3392 14.8336 18.2285 14.6438H18.2292Z"
                    fill="white"
                  />
                </svg>
              </div>
            </div>
            <div className="cursor-pointer">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="36"
                height="36"
                viewBox="0 0 36 36"
                fill="none"
              >
                <path
                  fill-rule="evenodd"
                  clip-rule="evenodd"
                  d="M11.1068 26.0355C16.2405 25.2855 19.7753 25.35 24.9158 26.0618C25.288 26.1157 25.6282 26.3026 25.8734 26.5878C26.1187 26.873 26.2524 27.2373 26.25 27.6135C26.25 27.9735 26.1262 28.323 25.9027 28.596C25.5132 29.072 25.1141 29.5401 24.7058 30H26.6865C26.811 29.8515 26.9362 29.7 27.063 29.5463C27.5079 29.0007 27.7506 28.3182 27.75 27.6143C27.75 26.0955 26.6415 24.7868 25.1213 24.5768C19.8592 23.8485 16.1813 23.7788 10.89 24.552C9.354 24.7763 8.25 26.1053 8.25 27.6345C8.25 28.3133 8.47125 28.9845 8.8905 29.5282C9.01425 29.6888 9.1365 29.8463 9.258 30.0008H11.1907C10.8108 29.5459 10.4402 29.0833 10.0793 28.6133C9.86472 28.3319 9.74899 27.9876 9.75 27.6338C9.75 26.826 10.3305 26.1488 11.1068 26.0355ZM18 18.75C18.5909 18.75 19.1761 18.6336 19.7221 18.4075C20.268 18.1813 20.7641 17.8498 21.182 17.432C21.5998 17.0141 21.9313 16.518 22.1575 15.9721C22.3836 15.4261 22.5 14.8409 22.5 14.25C22.5 13.6591 22.3836 13.0739 22.1575 12.5279C21.9313 11.982 21.5998 11.4859 21.182 11.068C20.7641 10.6502 20.268 10.3187 19.7221 10.0925C19.1761 9.8664 18.5909 9.75 18 9.75C16.8065 9.75 15.6619 10.2241 14.818 11.068C13.9741 11.9119 13.5 13.0565 13.5 14.25C13.5 15.4435 13.9741 16.5881 14.818 17.432C15.6619 18.2759 16.8065 18.75 18 18.75ZM18 20.25C19.5913 20.25 21.1174 19.6179 22.2426 18.4926C23.3679 17.3674 24 15.8413 24 14.25C24 12.6587 23.3679 11.1326 22.2426 10.0074C21.1174 8.88214 19.5913 8.25 18 8.25C16.4087 8.25 14.8826 8.88214 13.7574 10.0074C12.6321 11.1326 12 12.6587 12 14.25C12 15.8413 12.6321 17.3674 13.7574 18.4926C14.8826 19.6179 16.4087 20.25 18 20.25Z"
                  fill="#808080"
                />
                <path
                  fill-rule="evenodd"
                  clip-rule="evenodd"
                  d="M18 31.5C25.4557 31.5 31.5 25.4557 31.5 18C31.5 10.5443 25.4557 4.5 18 4.5C10.5443 4.5 4.5 10.5443 4.5 18C4.5 25.4557 10.5443 31.5 18 31.5ZM18 33C26.2845 33 33 26.2845 33 18C33 9.7155 26.2845 3 18 3C9.7155 3 3 9.7155 3 18C3 26.2845 9.7155 33 18 33Z"
                  fill="#808080"
                />
              </svg>
            </div>
          </div>
        </div>
        {/* content */}
        <div className="px-[16px] md:mx-auto md:w-[80%] lg:w-[70%]">
          <div className="clashmd pt-[140px] mb-[10px] md:mb-[8px] text-[24px] text-center md:text-left mx-auto md:mx-0 font-[500] tracking-[0.34px] md:text-[34px] text-[#fff]">
            Get people to follow you on {"Instagram"}
          </div>
          <div className="clashlt mb-[42px] md:mb-[60px] mx-auto text-center md:text-left md:mx-0 md:w-[70%] text-[15px] md:tracking-[0.32px] tracking-[0.3px] leading-[160%] md:text-[16px] font-[400] text-[#808080]">
            Want to see details of this task you created?{" "}
            <span
              onClick={goDetails}
              className="text-[#8e60cf] cursor-pointer clashmd font-[500]"
            >
              Click HERE
            </span>
            <br />{" "}
            <span className="text-[#cb29be] clashmd font-[500]">
              Please note:
            </span>{" "}
            any task result you leave unattended will be automatically accepted
            after 7 days.
          </div>
          {/* table md lg */}
          <div className="clashmd mb-[12px] text-[17px] md:text-[20.948px] font-[500] text-[#fff]">
            Result - {0}
          </div>
          <div className="w-full hidden md:block overflow-x-scroll side">
            <div className="rounded-b-[10px] w-fit lg:w-full border-[0.4px] border-[transparent] bg-[#121212]">
              <div className="text-[#fff] py-[14px] flex items-center w-fit lg:w-full text-left px-[20px] rounded-t-[10px] bg-[#333] text-[16px] clashmd font-[500]">
                <div className="lg:w-[10%] w-[200px]">S/N</div>
                <div className="lg:w-[30%] w-[800px]">
                  User/social media username
                </div>
                <div className="lg:w-[20%] w-[600px]">Proof of work</div>
                <div className="lg:w-[30%] w-[800px]">Date completed</div>
                <div className="lg:w-[10%] w-[200px]">Action</div>
              </div>
            </div>
            <div className="mt-[18px] md:mt-[20px] border-b border-[#333]"></div>
            <div className="py-[24px] rounded-b-[10px] border border-[#333] flex justify-between items-center px-[18px] md:px-[20px] md:py-[30px]">
              <div className="rounded-[8px] leading-[20px] clashmd font-[500] text-[#716f6f] text-[14px] w-fit px-[16px] cursor-pointer border border-[#373636] bg-[#333] py-[8px]">
                Previous
              </div>
              <div>{/* set records or pagination */}</div>
              <div className="rounded-[8px] leading-[20px] clashmd font-[500] text-[#121212] text-[14px] w-fit px-[16px] cursor-pointer border border-[#e6e6e7] bg-[#fff] py-[8px]">
                Next
              </div>
            </div>
          </div>
          {/* end table big screen */}
          {/* map list for sm screen */}
          <div className="w-full px-[16px] py-[23px] bg-[#121212] border border-[#333] rounded-[10px] md:hidden"></div>
          {/* end map list */}
        </div>
        {/* end body content */}
      </div>
    </body>
  );
};

export default Result;
