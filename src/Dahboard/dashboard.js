import React from "react";
import Homeside from "../components/Homeside";

const Home = () => {
  return (
    <div className="side min-h-[100vh] md:flex w-full px-10">
      {/* second side */}
      <div className="w-full px-[0px] md:flex md:justify-center md:px-[20px] md:relative md:left-[295px] lg:left-[295px] md:w-[calc(100%-295px)] lg:w-[calc(100%-295px)]">
        <div className="w-full pb-[20px] md:pt-[20px] md:pb-[20px]">
          <Homeside />
        </div>
      </div>
      {/* :)) empty */}
    </div>
  );
};

export default Home;