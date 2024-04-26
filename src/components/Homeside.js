import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const Homeside = () => {
  const navigate = useNavigate();
  const [fundbg, setFundbg] = useState(false);
  const toggleFund = () => {
    setFundbg((prev) => !prev);
  };
  const gotoResult = () => {
    navigate("/result");
  };
  return (
    <>
      <div className="md:flex w-full mb-[98px] items-center hidden justify-between">
        <div></div>
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
      <div className="bg-[#121212] items-center mb-[40px] flex justify-between py-[16.31px] px-[16.07px] md:hidden">
        <div className="text-[#fff] tracking-[0.169px] font-[500] clashmd text-[16.921px]">
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
      {/* content */}
      <div className="px-[21px] md:px-[0px]">
        <div className="text-[#fff] text-center md:text-left w-fit mx-auto md:mx-[0px] mb-[10px] tracking-[0.24px] md:tracking-[0.34px] font-[500] clashmd text-[24] md:text-[34px]">
          Dashboard
        </div>
        <div className="clashlt mb-[40px] md:mb-[60px] text-center w-full md:w-[75%] md:text-left tracking-[0.3px] md:tracking-[0.32px] leading-[160%] text-[15px] md:text-[16px] font-[400] text-[#808080]">
          Here you can keep track of your tasks, earnings, total balance,
          orders, transactions and so much more! You can{" "}
          <span onClick={toggleFund} className="cursor-pointer text-[#8e60cf]">
            Fund your Trendit account
          </span>{" "}
          to pay for tasks you create.
        </div>
      </div>
      <div className="w-full mb-[70px] md:mb-[60px] side overflow-x-scroll">
        <div className="pl-[16px] space-x-[16px] w-fit flex items-center md:pl-[0px]">
          {/* 1 */}
          <div className="border w-[293px] md:w-[360px] lg:w-[335px] border-[#333] px-[20px] py-[16px] bg-[#121212] rounded-[10px]">
            <div className="flex mb-[34px] items-center justify-between">
              <div className="rounded-[182.222px] p-[7.32px] bg-[#222]">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="27"
                  height="27"
                  viewBox="0 0 27 27"
                  fill="none"
                >
                  <path
                    fill-rule="evenodd"
                    clip-rule="evenodd"
                    d="M13.5215 3.61719C11.0412 3.61719 8.7811 4.43646 7.44402 5.10582C7.32322 5.16622 7.21065 5.22552 7.10577 5.28263C6.89821 5.39575 6.7214 5.50117 6.58083 5.59397L8.10185 7.83323L8.81789 8.11822C11.6161 9.52997 15.3687 9.52997 18.1675 8.11822L18.9802 7.6965L20.4189 5.59397C20.1208 5.39959 19.8109 5.22408 19.4909 5.06848C18.1609 4.40625 15.9552 3.61719 13.5215 3.61719ZM9.98364 6.15187C9.44503 6.05108 8.91306 5.91758 8.39068 5.75212C9.6432 5.19587 11.5102 4.60558 13.521 4.60558C14.9141 4.60558 16.2314 4.88892 17.3208 5.24804C16.0441 5.42759 14.6818 5.73235 13.3837 6.10739C12.3624 6.40281 11.1686 6.37096 9.98364 6.15187ZM18.7474 8.93254L18.6129 9.00063C15.534 10.5535 11.4509 10.5535 8.37201 9.00063L8.24462 8.93584C3.62004 14.0101 0.0892816 23.3834 13.5215 23.3834C26.9527 23.3834 23.3357 13.835 18.7474 8.93254ZM12.9505 13.5011C12.6592 13.5011 12.3799 13.6168 12.1739 13.8228C11.968 14.0287 11.8523 14.3081 11.8523 14.5993C11.8523 14.8906 11.968 15.1699 12.1739 15.3759C12.3799 15.5818 12.6592 15.6975 12.9505 15.6975V13.5011ZM14.0487 12.4029V11.8538H12.9505V12.4029C12.3679 12.4029 11.8093 12.6343 11.3974 13.0462C10.9854 13.4581 10.754 14.0168 10.754 14.5993C10.754 15.1819 10.9854 15.7405 11.3974 16.1524C11.8093 16.5643 12.3679 16.7958 12.9505 16.7958V18.9922C12.7233 18.9922 12.5018 18.9219 12.3163 18.7908C12.1309 18.6597 11.9906 18.4743 11.9149 18.2602C11.8664 18.1229 11.7653 18.0105 11.6339 17.9476C11.5025 17.8848 11.3515 17.8768 11.2142 17.9253C11.0769 17.9738 10.9644 18.0748 10.9016 18.2062C10.8388 18.3376 10.8307 18.4886 10.8792 18.6259C11.0307 19.0542 11.3112 19.425 11.6821 19.6873C12.0531 19.9496 12.4962 20.0904 12.9505 20.0904V20.6395H14.0487V20.0904C14.6312 20.0904 15.1899 19.859 15.6018 19.4471C16.0137 19.0352 16.2451 18.4765 16.2451 17.894C16.2451 17.3114 16.0137 16.7528 15.6018 16.3409C15.1899 15.929 14.6312 15.6975 14.0487 15.6975V13.5011C14.5264 13.5011 14.9333 13.8059 15.0848 14.2331C15.1073 14.303 15.1436 14.3676 15.1915 14.4233C15.2394 14.4789 15.298 14.5244 15.3638 14.5569C15.4296 14.5895 15.5013 14.6086 15.5746 14.613C15.6478 14.6174 15.7213 14.6071 15.7905 14.5827C15.8597 14.5582 15.9233 14.5201 15.9776 14.4706C16.0318 14.4211 16.0756 14.3613 16.1063 14.2946C16.137 14.2279 16.1541 14.1557 16.1564 14.0824C16.1587 14.009 16.1463 13.9359 16.1199 13.8674C15.9684 13.4391 15.6879 13.0683 15.317 12.806C14.9461 12.5437 14.503 12.4029 14.0487 12.4029ZM14.0487 16.7958V18.9922C14.3399 18.9922 14.6193 18.8765 14.8252 18.6705C15.0312 18.4646 15.1469 18.1852 15.1469 17.894C15.1469 17.6027 15.0312 17.3234 14.8252 17.1174C14.6193 16.9115 14.3399 16.7958 14.0487 16.7958Z"
                    fill="white"
                  />
                </svg>
              </div>
              <div className="bg-[#fff] cursor-pointer flex items-center space-x-[4px] w-fit py-[2px] px-[10px] rounded-[5px]">
                <div className="clashmd tracking-[0.28px] leading-[160%] text-[14px] font-[500] text-[#000]">
                  Withdraw
                </div>
                <div>
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="16"
                    height="16"
                    viewBox="0 0 16 16"
                    fill="none"
                  >
                    <path
                      fill-rule="evenodd"
                      clip-rule="evenodd"
                      d="M7.33333 13.3333C7.33333 13.1565 7.26309 12.987 7.13807 12.8619C7.01305 12.7369 6.84348 12.6667 6.66667 12.6667H3.33333V3.33333H6.66667C6.84348 3.33333 7.01305 3.2631 7.13807 3.13807C7.26309 3.01305 7.33333 2.84348 7.33333 2.66667C7.33333 2.48986 7.26309 2.32029 7.13807 2.19526C7.01305 2.07024 6.84348 2 6.66667 2H3.33333C2.97971 2 2.64057 2.14048 2.39052 2.39052C2.14048 2.64057 2 2.97971 2 3.33333V12.6667C2 13.0203 2.14048 13.3594 2.39052 13.6095C2.64057 13.8595 2.97971 14 3.33333 14H6.66667C6.84348 14 7.01305 13.9298 7.13807 13.8047C7.26309 13.6797 7.33333 13.5101 7.33333 13.3333Z"
                      fill="black"
                    />
                    <path
                      d="M14.476 8.46835C14.598 8.3444 14.6664 8.17756 14.6667 8.00368V7.99968C14.6663 7.82353 14.5961 7.65473 14.4713 7.53035L11.8047 4.86368C11.7432 4.80001 11.6696 4.74922 11.5883 4.71428C11.5069 4.67934 11.4195 4.66095 11.3309 4.66018C11.2424 4.65941 11.1546 4.67628 11.0727 4.7098C10.9908 4.74332 10.9163 4.79282 10.8537 4.85542C10.7912 4.91801 10.7416 4.99245 10.7081 5.07438C10.6746 5.15631 10.6577 5.2441 10.6585 5.33262C10.6593 5.42114 10.6777 5.50862 10.7126 5.58995C10.7475 5.67129 10.7983 5.74485 10.862 5.80635L12.3907 7.33501H6.00001C5.8232 7.33501 5.65363 7.40525 5.52861 7.53028C5.40358 7.6553 5.33334 7.82487 5.33334 8.00168C5.33334 8.17849 5.40358 8.34806 5.52861 8.47309C5.65363 8.59811 5.8232 8.66835 6.00001 8.66835H12.3907L10.862 10.197C10.7406 10.3227 10.6734 10.4912 10.6749 10.6659C10.6764 10.8407 10.7465 11.008 10.8701 11.1316C10.9937 11.2552 11.1609 11.3253 11.3357 11.3268C11.5105 11.3283 11.6789 11.2611 11.8047 11.1397L14.4713 8.47301L14.476 8.46835Z"
                      fill="black"
                    />
                  </svg>
                </div>
              </div>
            </div>
            <div className="clashlt mb-[6px] tracking-[0.18px] text-[18px] font-[400] text-[#808080]">
              Current balance
            </div>
            <div className="flex items-center justify-between">
              <div className="clashmd text-[30px] tracking-[0.3px] font-[500] text-[#fff]">
                $1,000.00
              </div>
              <div className="space-y-[2px]">
                <div className="flex items-center space-x-[4px]">
                  <div>
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="24"
                      height="24"
                      viewBox="0 0 24 24"
                      fill="none"
                    >
                      <path
                        d="M2.69999 17.3C2.51665 17.1167 2.42499 16.8873 2.42499 16.612C2.42499 16.3367 2.51665 16.0993 2.69999 15.9L8.69999 9.85C8.79999 9.76667 8.90832 9.7 9.02499 9.65C9.14165 9.6 9.26665 9.575 9.39999 9.575C9.53332 9.575 9.66232 9.6 9.78699 9.65C9.91165 9.7 10.016 9.76667 10.1 9.85L13.4 13.15L18.6 8H17C16.7167 8 16.479 7.904 16.287 7.712C16.095 7.52 15.9993 7.28267 16 7C16 6.71667 16.096 6.479 16.288 6.287C16.48 6.095 16.7173 5.99934 17 6H21C21.2833 6 21.521 6.096 21.713 6.288C21.905 6.48 22.0007 6.71734 22 7V11C22 11.2833 21.904 11.521 21.712 11.713C21.52 11.905 21.2827 12.0007 21 12C20.7167 12 20.479 11.904 20.287 11.712C20.095 11.52 19.9993 11.2827 20 11V9.4L14.1 15.3C14 15.4 13.8917 15.471 13.775 15.513C13.6583 15.555 13.5333 15.5757 13.4 15.575C13.2667 15.575 13.1417 15.5543 13.025 15.513C12.9083 15.4717 12.8 15.4007 12.7 15.3L9.39999 12L4.07499 17.325C3.89165 17.5083 3.66665 17.6 3.39999 17.6C3.13332 17.6 2.89999 17.5 2.69999 17.3Z"
                        fill="#3A9800"
                      />
                    </svg>
                  </div>
                  <div className="clashmd tracking-[0.16px] font-[500] text-[16px] text-[#3a9800]">
                    16%
                  </div>
                </div>
                <div className="clashlt tracking-[0.14px] text-[14px] font-[400] text-[#808080]">
                  vs last 30 days
                </div>
              </div>
            </div>
          </div>
          {/* end 1 */}
          {/* 2 */}
          <div className="border w-[293px] md:w-[360px] lg:w-[335px] border-[#333] px-[20px] py-[16px] bg-[#121212] rounded-[10px]">
            <div className="flex mb-[34px] items-center justify-between">
              <div className="rounded-[182.222px] p-[7.32px] bg-[#222]">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="27"
                  height="27"
                  viewBox="0 0 27 27"
                  fill="none"
                >
                  <path
                    fill-rule="evenodd"
                    clip-rule="evenodd"
                    d="M13.5215 3.61719C11.0412 3.61719 8.7811 4.43646 7.44402 5.10582C7.32322 5.16622 7.21065 5.22552 7.10577 5.28263C6.89821 5.39575 6.7214 5.50117 6.58083 5.59397L8.10185 7.83323L8.81789 8.11822C11.6161 9.52997 15.3687 9.52997 18.1675 8.11822L18.9802 7.6965L20.4189 5.59397C20.1208 5.39959 19.8109 5.22408 19.4909 5.06848C18.1609 4.40625 15.9552 3.61719 13.5215 3.61719ZM9.98364 6.15187C9.44503 6.05108 8.91306 5.91758 8.39068 5.75212C9.6432 5.19587 11.5102 4.60558 13.521 4.60558C14.9141 4.60558 16.2314 4.88892 17.3208 5.24804C16.0441 5.42759 14.6818 5.73235 13.3837 6.10739C12.3624 6.40281 11.1686 6.37096 9.98364 6.15187ZM18.7474 8.93254L18.6129 9.00063C15.534 10.5535 11.4509 10.5535 8.37201 9.00063L8.24462 8.93584C3.62004 14.0101 0.0892816 23.3834 13.5215 23.3834C26.9527 23.3834 23.3357 13.835 18.7474 8.93254ZM12.9505 13.5011C12.6592 13.5011 12.3799 13.6168 12.1739 13.8228C11.968 14.0287 11.8523 14.3081 11.8523 14.5993C11.8523 14.8906 11.968 15.1699 12.1739 15.3759C12.3799 15.5818 12.6592 15.6975 12.9505 15.6975V13.5011ZM14.0487 12.4029V11.8538H12.9505V12.4029C12.3679 12.4029 11.8093 12.6343 11.3974 13.0462C10.9854 13.4581 10.754 14.0168 10.754 14.5993C10.754 15.1819 10.9854 15.7405 11.3974 16.1524C11.8093 16.5643 12.3679 16.7958 12.9505 16.7958V18.9922C12.7233 18.9922 12.5018 18.9219 12.3163 18.7908C12.1309 18.6597 11.9906 18.4743 11.9149 18.2602C11.8664 18.1229 11.7653 18.0105 11.6339 17.9476C11.5025 17.8848 11.3515 17.8768 11.2142 17.9253C11.0769 17.9738 10.9644 18.0748 10.9016 18.2062C10.8388 18.3376 10.8307 18.4886 10.8792 18.6259C11.0307 19.0542 11.3112 19.425 11.6821 19.6873C12.0531 19.9496 12.4962 20.0904 12.9505 20.0904V20.6395H14.0487V20.0904C14.6312 20.0904 15.1899 19.859 15.6018 19.4471C16.0137 19.0352 16.2451 18.4765 16.2451 17.894C16.2451 17.3114 16.0137 16.7528 15.6018 16.3409C15.1899 15.929 14.6312 15.6975 14.0487 15.6975V13.5011C14.5264 13.5011 14.9333 13.8059 15.0848 14.2331C15.1073 14.303 15.1436 14.3676 15.1915 14.4233C15.2394 14.4789 15.298 14.5244 15.3638 14.5569C15.4296 14.5895 15.5013 14.6086 15.5746 14.613C15.6478 14.6174 15.7213 14.6071 15.7905 14.5827C15.8597 14.5582 15.9233 14.5201 15.9776 14.4706C16.0318 14.4211 16.0756 14.3613 16.1063 14.2946C16.137 14.2279 16.1541 14.1557 16.1564 14.0824C16.1587 14.009 16.1463 13.9359 16.1199 13.8674C15.9684 13.4391 15.6879 13.0683 15.317 12.806C14.9461 12.5437 14.503 12.4029 14.0487 12.4029ZM14.0487 16.7958V18.9922C14.3399 18.9922 14.6193 18.8765 14.8252 18.6705C15.0312 18.4646 15.1469 18.1852 15.1469 17.894C15.1469 17.6027 15.0312 17.3234 14.8252 17.1174C14.6193 16.9115 14.3399 16.7958 14.0487 16.7958Z"
                    fill="white"
                  />
                </svg>
              </div>
              <div className="bg-[#fff] hidden cursor-pointer items-center space-x-[4px] w-fit py-[2px] px-[10px] rounded-[5px]">
                <div className="clashmd tracking-[0.28px] leading-[160%] text-[14px] font-[500] text-[#000]">
                  Withdraw
                </div>
                <div>
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="16"
                    height="16"
                    viewBox="0 0 16 16"
                    fill="none"
                  >
                    <path
                      fill-rule="evenodd"
                      clip-rule="evenodd"
                      d="M7.33333 13.3333C7.33333 13.1565 7.26309 12.987 7.13807 12.8619C7.01305 12.7369 6.84348 12.6667 6.66667 12.6667H3.33333V3.33333H6.66667C6.84348 3.33333 7.01305 3.2631 7.13807 3.13807C7.26309 3.01305 7.33333 2.84348 7.33333 2.66667C7.33333 2.48986 7.26309 2.32029 7.13807 2.19526C7.01305 2.07024 6.84348 2 6.66667 2H3.33333C2.97971 2 2.64057 2.14048 2.39052 2.39052C2.14048 2.64057 2 2.97971 2 3.33333V12.6667C2 13.0203 2.14048 13.3594 2.39052 13.6095C2.64057 13.8595 2.97971 14 3.33333 14H6.66667C6.84348 14 7.01305 13.9298 7.13807 13.8047C7.26309 13.6797 7.33333 13.5101 7.33333 13.3333Z"
                      fill="black"
                    />
                    <path
                      d="M14.476 8.46835C14.598 8.3444 14.6664 8.17756 14.6667 8.00368V7.99968C14.6663 7.82353 14.5961 7.65473 14.4713 7.53035L11.8047 4.86368C11.7432 4.80001 11.6696 4.74922 11.5883 4.71428C11.5069 4.67934 11.4195 4.66095 11.3309 4.66018C11.2424 4.65941 11.1546 4.67628 11.0727 4.7098C10.9908 4.74332 10.9163 4.79282 10.8537 4.85542C10.7912 4.91801 10.7416 4.99245 10.7081 5.07438C10.6746 5.15631 10.6577 5.2441 10.6585 5.33262C10.6593 5.42114 10.6777 5.50862 10.7126 5.58995C10.7475 5.67129 10.7983 5.74485 10.862 5.80635L12.3907 7.33501H6.00001C5.8232 7.33501 5.65363 7.40525 5.52861 7.53028C5.40358 7.6553 5.33334 7.82487 5.33334 8.00168C5.33334 8.17849 5.40358 8.34806 5.52861 8.47309C5.65363 8.59811 5.8232 8.66835 6.00001 8.66835H12.3907L10.862 10.197C10.7406 10.3227 10.6734 10.4912 10.6749 10.6659C10.6764 10.8407 10.7465 11.008 10.8701 11.1316C10.9937 11.2552 11.1609 11.3253 11.3357 11.3268C11.5105 11.3283 11.6789 11.2611 11.8047 11.1397L14.4713 8.47301L14.476 8.46835Z"
                      fill="black"
                    />
                  </svg>
                </div>
              </div>
            </div>
            <div className="clashlt mb-[6px] tracking-[0.18px] text-[18px] font-[400] text-[#808080]">
              Total earnings this month
            </div>
            <div className="flex items-center justify-between">
              <div className="clashmd text-[30px] tracking-[0.3px] font-[500] text-[#fff]">
                $900.00
              </div>
              <div className="space-y-[2px]">
                <div className="flex items-center space-x-[4px]">
                  <div>
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="24"
                      height="24"
                      viewBox="0 0 24 24"
                      fill="none"
                    >
                      <path
                        d="M2.69999 17.3C2.51665 17.1167 2.42499 16.8873 2.42499 16.612C2.42499 16.3367 2.51665 16.0993 2.69999 15.9L8.69999 9.85C8.79999 9.76667 8.90832 9.7 9.02499 9.65C9.14165 9.6 9.26665 9.575 9.39999 9.575C9.53332 9.575 9.66232 9.6 9.78699 9.65C9.91165 9.7 10.016 9.76667 10.1 9.85L13.4 13.15L18.6 8H17C16.7167 8 16.479 7.904 16.287 7.712C16.095 7.52 15.9993 7.28267 16 7C16 6.71667 16.096 6.479 16.288 6.287C16.48 6.095 16.7173 5.99934 17 6H21C21.2833 6 21.521 6.096 21.713 6.288C21.905 6.48 22.0007 6.71734 22 7V11C22 11.2833 21.904 11.521 21.712 11.713C21.52 11.905 21.2827 12.0007 21 12C20.7167 12 20.479 11.904 20.287 11.712C20.095 11.52 19.9993 11.2827 20 11V9.4L14.1 15.3C14 15.4 13.8917 15.471 13.775 15.513C13.6583 15.555 13.5333 15.5757 13.4 15.575C13.2667 15.575 13.1417 15.5543 13.025 15.513C12.9083 15.4717 12.8 15.4007 12.7 15.3L9.39999 12L4.07499 17.325C3.89165 17.5083 3.66665 17.6 3.39999 17.6C3.13332 17.6 2.89999 17.5 2.69999 17.3Z"
                        fill="#3A9800"
                      />
                    </svg>
                  </div>
                  <div className="clashmd tracking-[0.16px] font-[500] text-[16px] text-[#3a9800]">
                    16%
                  </div>
                </div>
                <div className="clashlt tracking-[0.14px] text-[14px] font-[400] text-[#808080]">
                  vs last 30 days
                </div>
              </div>
            </div>
          </div>
          {/* end 2 */}
          {/* 3 */}
          <div className="border w-[293px] md:w-[360px] lg:w-[335px] border-[#333] px-[20px] py-[16px] bg-[#121212] rounded-[10px]">
            <div className="flex mb-[34px] items-center justify-between">
              <div className="rounded-[182.222px] p-[7.32px] bg-[#222]">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="27"
                  height="27"
                  viewBox="0 0 27 27"
                  fill="none"
                >
                  <path
                    d="M12.521 3.95312V9.22512H3.95398V7.90712C3.95398 6.85846 4.37056 5.85274 5.11208 5.11122C5.8536 4.36971 6.85931 3.95313 7.90798 3.95312H12.521ZM13.839 3.95312V15.8151H22.406V7.90712C22.406 6.85846 21.9894 5.85274 21.2479 5.11122C20.5064 4.36971 19.5006 3.95313 18.452 3.95312H13.839ZM22.406 17.1331H13.839V22.4051H18.452C19.5006 22.4051 20.5064 21.9885 21.2479 21.247C21.9894 20.5055 22.406 19.4998 22.406 18.4511V17.1331ZM12.521 22.4051V10.5431H3.95398V18.4511C3.95398 19.4998 4.37056 20.5055 5.11208 21.247C5.8536 21.9885 6.85931 22.4051 7.90798 22.4051H12.521Z"
                    fill="white"
                  />
                </svg>
              </div>
              <div className="bg-[#fff] hidden cursor-pointer items-center space-x-[4px] w-fit py-[2px] px-[10px] rounded-[5px]">
                <div className="clashmd tracking-[0.28px] leading-[160%] text-[14px] font-[500] text-[#000]">
                  Withdraw
                </div>
                <div>
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="16"
                    height="16"
                    viewBox="0 0 16 16"
                    fill="none"
                  >
                    <path
                      fill-rule="evenodd"
                      clip-rule="evenodd"
                      d="M7.33333 13.3333C7.33333 13.1565 7.26309 12.987 7.13807 12.8619C7.01305 12.7369 6.84348 12.6667 6.66667 12.6667H3.33333V3.33333H6.66667C6.84348 3.33333 7.01305 3.2631 7.13807 3.13807C7.26309 3.01305 7.33333 2.84348 7.33333 2.66667C7.33333 2.48986 7.26309 2.32029 7.13807 2.19526C7.01305 2.07024 6.84348 2 6.66667 2H3.33333C2.97971 2 2.64057 2.14048 2.39052 2.39052C2.14048 2.64057 2 2.97971 2 3.33333V12.6667C2 13.0203 2.14048 13.3594 2.39052 13.6095C2.64057 13.8595 2.97971 14 3.33333 14H6.66667C6.84348 14 7.01305 13.9298 7.13807 13.8047C7.26309 13.6797 7.33333 13.5101 7.33333 13.3333Z"
                      fill="black"
                    />
                    <path
                      d="M14.476 8.46835C14.598 8.3444 14.6664 8.17756 14.6667 8.00368V7.99968C14.6663 7.82353 14.5961 7.65473 14.4713 7.53035L11.8047 4.86368C11.7432 4.80001 11.6696 4.74922 11.5883 4.71428C11.5069 4.67934 11.4195 4.66095 11.3309 4.66018C11.2424 4.65941 11.1546 4.67628 11.0727 4.7098C10.9908 4.74332 10.9163 4.79282 10.8537 4.85542C10.7912 4.91801 10.7416 4.99245 10.7081 5.07438C10.6746 5.15631 10.6577 5.2441 10.6585 5.33262C10.6593 5.42114 10.6777 5.50862 10.7126 5.58995C10.7475 5.67129 10.7983 5.74485 10.862 5.80635L12.3907 7.33501H6.00001C5.8232 7.33501 5.65363 7.40525 5.52861 7.53028C5.40358 7.6553 5.33334 7.82487 5.33334 8.00168C5.33334 8.17849 5.40358 8.34806 5.52861 8.47309C5.65363 8.59811 5.8232 8.66835 6.00001 8.66835H12.3907L10.862 10.197C10.7406 10.3227 10.6734 10.4912 10.6749 10.6659C10.6764 10.8407 10.7465 11.008 10.8701 11.1316C10.9937 11.2552 11.1609 11.3253 11.3357 11.3268C11.5105 11.3283 11.6789 11.2611 11.8047 11.1397L14.4713 8.47301L14.476 8.46835Z"
                      fill="black"
                    />
                  </svg>
                </div>
              </div>
            </div>
            <div className="clashlt mb-[6px] tracking-[0.18px] text-[18px] font-[400] text-[#808080]">
              Tasks done this month
            </div>
            <div className="flex items-center justify-between">
              <div className="clashmd text-[30px] tracking-[0.3px] font-[500] text-[#fff]">
                100
              </div>
              <div className="space-y-[2px]">
                <div className="flex items-center space-x-[4px]">
                  <div>
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="24"
                      height="24"
                      viewBox="0 0 24 24"
                      fill="none"
                    >
                      <path
                        d="M2.69999 17.3C2.51665 17.1167 2.42499 16.8873 2.42499 16.612C2.42499 16.3367 2.51665 16.0993 2.69999 15.9L8.69999 9.85C8.79999 9.76667 8.90832 9.7 9.02499 9.65C9.14165 9.6 9.26665 9.575 9.39999 9.575C9.53332 9.575 9.66232 9.6 9.78699 9.65C9.91165 9.7 10.016 9.76667 10.1 9.85L13.4 13.15L18.6 8H17C16.7167 8 16.479 7.904 16.287 7.712C16.095 7.52 15.9993 7.28267 16 7C16 6.71667 16.096 6.479 16.288 6.287C16.48 6.095 16.7173 5.99934 17 6H21C21.2833 6 21.521 6.096 21.713 6.288C21.905 6.48 22.0007 6.71734 22 7V11C22 11.2833 21.904 11.521 21.712 11.713C21.52 11.905 21.2827 12.0007 21 12C20.7167 12 20.479 11.904 20.287 11.712C20.095 11.52 19.9993 11.2827 20 11V9.4L14.1 15.3C14 15.4 13.8917 15.471 13.775 15.513C13.6583 15.555 13.5333 15.5757 13.4 15.575C13.2667 15.575 13.1417 15.5543 13.025 15.513C12.9083 15.4717 12.8 15.4007 12.7 15.3L9.39999 12L4.07499 17.325C3.89165 17.5083 3.66665 17.6 3.39999 17.6C3.13332 17.6 2.89999 17.5 2.69999 17.3Z"
                        fill="#3A9800"
                      />
                    </svg>
                  </div>
                  <div className="clashmd tracking-[0.16px] font-[500] text-[16px] text-[#3a9800]">
                    9%
                  </div>
                </div>
                <div className="clashlt tracking-[0.14px] text-[14px] font-[400] text-[#808080]">
                  vs last 30 days
                </div>
              </div>
            </div>
          </div>
          {/* end 3 */}
        </div>
      </div>
      {/* task created */}
      <div className="px-[16px] md:px-[0px]">
        <div className="clashmd mb-[14px] md:mb-[12px] text-[18px] md:text-[20.948px] font-[500] text-[#fff]">
          Task created by you
        </div>
        <div className="rounded-[10px] md:mb-[60px] mb-[50px] md:py-[20px] md:px-[30px] py-[18px] px-[16px] bg-[#121212] border border-[#333] w-full">
          <div className="flex w-full items-center">
            <div className="w-[70%] space-x-[10px] flex items-center">
              <div className="lg:w-[5%] w-[10%]">
                <img src="/img/whatsappicon.svg" alt="" className="" />
              </div>
              <div className="lg:w-[95%] w-[90%] space-y-[1px]">
                <div className="text-[#fff] text-[15px] tracking-[0.16px] font-[500] md:text-[16px] clashmd">
                  Get people to join your {"Whatsapp"} group
                </div>
                <div className="text-[13px] clashlt tracking-[0.26px] leading-[160%] font-[400] text-[#808080]">
                  09 May 2023
                </div>
              </div>
            </div>
            <div
              onClick={gotoResult}
              className="text-right w-[30%] float-right tracking-[0.16px] cursor-pointer clashmd font-[500] text-[15px] md:text-[16px] text-[#8e60cf]"
            >
              View result
            </div>
          </div>
        </div>
        {/* creation of table in task */}
        <div className="flex items-center justify-between">
          <div className="text-[18px] clashmd font-[500] md:text-[20.984px] text-[#fff]">
            My task history {0}
          </div>
          <div className="flex cursor-pointer items-center space-x-[2px]">
            <div>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="20"
                height="20"
                viewBox="0 0 20 20"
                fill="none"
              >
                <path
                  d="M15.8334 5H4.16669C3.25002 5 3.00002 5.5 3.66669 6.16667L7.16669 9.66667C7.83336 10.3333 8.33336 11.5833 8.33336 12.5V16.6667L11.6667 15V12.0833C11.6667 11.4167 12.1667 10.3333 12.8334 9.66667L16.3334 6.16667C17 5.5 16.75 5 15.8334 5Z"
                  fill="#808080"
                />
              </svg>
            </div>
            <div className="clashlt cursor-pointer tracking-[0.16px] text-[16px] font-[400] text-[#808080]">
              Filter
            </div>
          </div>
        </div>
        <div className="w-full overflow-x-scroll side">
          <div className="rounded-b-[10px] w-fit lg:w-full border-[0.4px] border-[transparent] bg-[#121212]">
            <div className="text-[#fff] flex items-center w-fit lg:w-full text-left px-[20px] rounded-t-[10px] bg-[#333] text-[16px] clashmd font-[500]">
              <div className="lg:w-[10%] w-[200px]">S/N</div>
              <div className="lg:w-[30%] w-[800px]">Task type</div>
              <div className="lg:w-[20%] w-[600px]">Date completed</div>
              <div className="lg:w-[30%] w-[800px]">Status</div>
              <div className="lg:w-[10%] w-[200px]">Payment due</div>
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
        {/* end creation of table */}
      </div>
      {/* end task */}
      {/* fund wallet */}
      <div
        className={`${
          fundbg ? "block" : "hidden"
        } fixed z-[100] left-0 px-[16px] md:px-[0px] flex justify-center items-center overlay_bg top-0 w-full h-full`}
      >
        <div className="w-full md:mx-auto border border-[#666] rounded-[10px] bg-[#000] py-[18px] px-[20px] md:w-[40%] lg:w-[30%]">
          <div className="flex mb-[40px] md:mb-[32px] itmes-center justify-between">
            <div onClick={toggleFund} className="cursor-pointer">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="20"
                height="20"
                viewBox="0 0 20 20"
                fill="none"
              >
                <path
                  d="M9.06268 16.082L3.56268 10.582C3.47934 10.4987 3.42018 10.4084 3.38518 10.3112C3.35018 10.2139 3.33295 10.1098 3.33351 9.99867C3.33351 9.88756 3.35101 9.78339 3.38601 9.68617C3.42101 9.58894 3.4799 9.49867 3.56268 9.41533L9.06268 3.91533C9.21545 3.76256 9.40656 3.68283 9.63601 3.67617C9.86545 3.6695 10.0632 3.74922 10.2293 3.91533C10.396 4.06811 10.483 4.25922 10.4902 4.48867C10.4974 4.71811 10.4174 4.91589 10.2502 5.082L6.16684 9.16533H15.4793C15.7155 9.16533 15.9135 9.24533 16.0735 9.40533C16.2335 9.56533 16.3132 9.76311 16.3127 9.99867C16.3127 10.2348 16.233 10.4328 16.0735 10.5928C15.9141 10.7528 15.716 10.8326 15.4793 10.832H6.16684L10.2502 14.9153C10.403 15.0681 10.483 15.2626 10.4902 15.4987C10.4974 15.7348 10.4174 15.9292 10.2502 16.082C10.0974 16.2487 9.90295 16.332 9.66684 16.332C9.43073 16.332 9.22934 16.2487 9.06268 16.082Z"
                  fill="white"
                />
              </svg>
            </div>
            <div className="text-[14px] tracking-[0.3px] clashmd font-[500] md:text-[16px] text-[#fff]">
              Fund wallet
            </div>
            <div></div>
          </div>
          <div className="clashlt tracking-[0.28px] mb-[4px] leading-[160%] font-[400] text-[14px] input_label">
            Amount
          </div>
          <div className="flex mb-[8px] w-full space-x-[11px]">
            <div className="w-[35%]">
              <select className="border focus:outline-none w-full clashlt tracking-[0.32px] leading-[160%] text-[#fff] font-[400] text-[16px] p-[11px] bg-[transparent] rounded-[10px] border-[#4c4c4c]">
                <option>{"CAD"}</option>
              </select>
            </div>
            <div className="w-[65%]">
              <input
                type="number"
                placeholder="50"
                className="w-full bg-[transparent] tracking-[0.3px] leading-[160%] clashlt font-[400] text-[#fff] p-[8px] border-[#4c4c4c] border rounded-[10px] focus:outline-none"
              />
            </div>
          </div>
          <div className="text-[13px] mb-[22px] tracking-[0.2px] leading-[160%] clashlt font-[400] text-[#808080]">
            Your wallet can be funded through your preferred payment method such
            as card payment, bank transfer, USSD etc.
          </div>
          <button className="bg-[#8e60cf] tracking-[0.16px] md:text-[16px] text-[14px] clashmd font-[500] text-[#fff] w-full text-center py-[13px] rounded-[10px]">
            Proceed
          </button>
        </div>
      </div>
      {/* end fund wallet */}
    </>
  );
};

export default Homeside;