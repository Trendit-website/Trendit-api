import React, { useState, useEffect } from "react";
import { ArrowForwardIcon } from "@chakra-ui/icons";
import locationData from "./LocationArray";

import {
  Button,
  FormControl,
  FormLabel,
  Input,
  Text,
  Select,
  Grid,
  Flex,
  Image,
  Container,
  useToast,
} from "@chakra-ui/react";
import { Link, useNavigate } from "react-router-dom";
import { ArrowBackIcon } from "@chakra-ui/icons";

import { Center, Heading } from "@chakra-ui/react";
import { Stack, HStack } from "@chakra-ui/react";
import Loader from "../../Loader";

import { Box, InputGroup, InputRightElement, VStack } from "@chakra-ui/react";
import { ViewIcon, ViewOffIcon } from "@chakra-ui/icons";
import { Spinner } from "@chakra-ui/react";

import Onboard from "../../assets/images/onboard.png";
import {
  useRegisterMutation,
  useResendCodeMutation,
  useVerifyEmailMutation,
} from "../../services/routes/authRoute";
import { isStrongPassword, isValidEmail } from "../../utils";
import {
  useGetCountriesQuery,
  useLazyGetLocalsQuery,
  useLazyGetStatesQuery,
} from "../../services/routes/locationRoute";

function SignUpComponent() {
  const navigate = useNavigate();
  const toast = useToast();
  const { data } = useGetCountriesQuery();
  const [trigger, { isLoading: stateLoad }] = useLazyGetStatesQuery();
  const [triggerForLocalsQuery, { isLoading: localLoad }] =
    useLazyGetLocalsQuery();
  // console.log  (data)
  const [register, { isLoading }] = useRegisterMutation();
  const [verifyEmail, { isLoading: mailLoading }] = useVerifyEmailMutation();
  const [resendCode, { isLoading: codeLoad }] = useResendCodeMutation();
  const [currentStep, setCurrentStep] = useState(1);

  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password1, setPassword1] = useState("");
  const [password2, setPassword2] = useState("");
  const [token, setToken] = useState("");
  const [selectedCountry, setSelectedCountry] = useState("");
  const [fetchedStates, setFetchedStates] = useState([]);
  const [fetchedLocals, setFetchedLocals] = useState([]); // State to store the selected country
  const [selectedState, setSelectedState] = useState(""); // State to store the selected state
  const [selectedCity, setSelectedCity] = useState("");
  const [selectedGender, setSelectedGender] = useState("");
  const [countryError, setCountryError] = useState("");
  const [stateError, setStateError] = useState("");
  const [cityError, setCityError] = useState("");
  const [genderError, setgenderError] = useState("");
  const [pin, setPin] = useState(["", "", "", "", "", ""]);
  const [error, setError] = useState("");
  const [resendSuccess, setResendSuccess] = useState(false);

  // Function to go back to the previous step

  const handlePreviousStep = () => {
    setCurrentStep(currentStep - 1);
  };

  // Function to handle gender selection
  const handleGenderChange = (event) => {
    setSelectedGender(event.target.value);
    setgenderError(""); // Reset the Gender error
  };

  const handleCountryChange = async (event) => {
    const selectedCountry = event.target.value;
    setSelectedCountry(selectedCountry);
    try {
      const res = await trigger(selectedCountry).unwrap();
      setFetchedStates(res.states);
      console.log(fetchedStates);
    } catch (error) {
      console.log(error);
    }

    setSelectedState(""); // Reset selected state when changing the country
    setSelectedCity(""); // Reset selected city when changing the country
    setCountryError(""); // Reset the country error
  };

  const handleStateChange = async (event) => {
    const selectedState = event.target.value;
    setSelectedState(selectedState);
    try {
      const res = await triggerForLocalsQuery(selectedState).unwrap();
      setFetchedLocals(res.state_lga);
      console.log(res);
    } catch (error) {
      console.log(error);
    }
    setSelectedCity(""); // Reset selected city when changing the country
    setStateError(""); // Reset the state error
  };

  const handleCityChange = (event) => {
    setSelectedCity(event.target.value);
    setCityError(""); // Reset the city error
  };
  //locationData.map((data) => data.country);
  // Create arrays of countries, states, and cities based on the selected values
  const countries = data?.countries.map((data) => data.name);
  const states = fetchedStates?.map((state) => state.name) || [];
  const cities = fetchedLocals?.map((state) => state) || [];
  // const cities =
  //   locationData
  //     .find((data) => data.country === selectedCountry)
  //     ?.states.find((state) => state.state === selectedState)?.cities || [];

  // Define CSS styles for the dropdown options
  const dropdownOptionStyles = {
    color: "#121212", // Change the text color as needed
  };

  // States to handle the code verificaation step

  const handlePinChange = (e, index) => {
    const updatedPin = [...pin];
    updatedPin[index] = e.target.value;

    // Check if the input exceeds a length of 1
    const inputValue = e.target.value;
    if (inputValue.length > 1) {
      // If it does, only take the first character
      updatedPin[index] = inputValue.charAt(0);
    } else {
      updatedPin[index] = inputValue;
    }
    setPin(updatedPin);
    setError("");
    setResendSuccess(false);

    // Automatically focus on the next input if available
    if (index < 5 && e.target.value !== "") {
      document.getElementById(`pin${index + 1}`).focus();
    } else if (index > 0 && e.target.value === "") {
      document.getElementById(`pin${index - 1}`).focus();
    }
  };

  // Function to check if the PIN input is filled
  const isPinFilled = () => {
    return pin.every((digit) => digit.trim() !== "");
  };

  useEffect(() => {
    // This effect runs after each render
    if (resendSuccess) {
      console.log("Resend successful. Clearing PIN input.");
      // Clear the PIN input if resendSuccess is true
      setPin(["", "", "", "", "", ""]);
    }
  }, [resendSuccess]);

  // Define the specific six-digit PIN that should be matched
  // Function to check if the pin matches before verying users
  const handleNextStep = async () => {
    if (currentStep === 1) {
      // Check for empty fields
      if (
        !username.trim() ||
        !email.trim() ||
        !password1.trim() ||
        !password2.trim()
      ) {
        toast({
          title: "Error",
          description: "Please fill all fields",
          status: "error",
          duration: 5000,
          isClosable: true,
        });
      } else if (!isValidEmail(email)) {
        toast({
          title: "Error",
          description: "Invalid email address",
          status: "error",
          duration: 5000,
          isClosable: true,
        });
      } else if (isStrongPassword(password1 || password2)) {
        toast({
          title: "Error",
          description: "Please enter a strong password",
          status: "error",
          duration: 5000,
          isClosable: true,
        });
      } else if (password1 !== password2) {
        toast({
          title: "Error",
          description: "Passwords do not match",
          status: "error",
          duration: 5000,
          isClosable: true,
        });
      } else {
        setCurrentStep((curr) => curr + 1);
      }
    }

    if (currentStep === 2) {
      if (!selectedGender.trim()) {
        toast({
          title: "Error",
          description: "Please select a gender.",
          status: "error",
          duration: 5000,
          isClosable: true,
        });
        return;
      }

      if (!selectedCountry.trim()) {
        toast({
          title: "Error",
          description: "Please select a Country.",
          status: "error",
          duration: 5000,
          isClosable: true,
        });
        return;
      }

      if (!selectedState.trim()) {
        toast({
          title: "Error",
          description: "Please select a State.",
          status: "error",
          duration: 5000,
          isClosable: true,
        });
        return;
      }

      if (!selectedCity.trim()) {
        toast({
          title: "Error",
          description: "Please select a city.",
          status: "error",
          duration: 5000,
          isClosable: true,
        });
        return;
      }

      const data = {
        username,
        email,
        password: password1,
        gender: selectedGender,
        local_government: selectedCity,
        country: selectedCountry,
        state: selectedState,
      };

      try {
        const res = await register(data).unwrap();
        toast({
          title: "Success",
          description: `${res.message}`,
          status: "success",
          duration: 5000,
          isClosable: true,
        });
        setToken(res.signup_token);
        console.log(res);
        setTimeout(() => {
          setCurrentStep(currentStep + 1); // Proceed to Step 3 after 3 seconds
        }, 3000);
      } catch (error) {
        console.log(error);
        toast({
          title: "Error",
          description: `${error?.data?.message || error?.error}`,
          status: "error",
          duration: 5000,
          isClosable: true,
        });
      }
    }
  };

  const handleVerifyEmail = async () => {
    const entered_code = pin.join(""); // Combine the array into a string
    setError("");

    try {
      console.log({
        signup_token: token,
        entered_code: parseInt(entered_code),
      });
      const res = await verifyEmail({
        signup_token: token,
        entered_code: parseInt(entered_code),
      }).unwrap();
      console.log(res);
      navigate("/log-in");
    } catch (error) {
      console.log(error);
      toast({
        title: "Error",
        description: `${error?.data?.message || error?.error}`,
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    }
  };

  // Function to handle resending of code
  const handleResendClick = async () => {
    const data = {
      signup_token: token,
    };
    try {
      const res = await resendCode(data).unwrap();
      console.log(res);
    } catch (error) {
      toast({
        title: "Error",
        description: `${error?.data?.message || error?.error}`,
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    }
  };

  // Function to collect and log step 1 and step 2 input values into console
  const logInputs = () => {
    console.log("Step 1 Inputs:");
    console.log("Username:", username);
    console.log("Email:", email);
    console.log("Password1:", password1);
    console.log("Password2:", password2);

    console.log("Step 2 Inputs:");
    console.log("Gender:", selectedGender);
    console.log("Country:", selectedCountry);
    console.log("State:", selectedState);
    console.log("City:", selectedCity);
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        //First registration step. Uesernmae, email and password
        return (
          <Flex
            color="white"
            display="flex"
            bg="black"
            alignItems="center"
            justifyContent="center"
            mt="25px"
            fontFamily="clash grotesk"
          >
            <VStack spacing={6} width={{ base: "80%", md: "500px" }}>
              <Box>
                <Text
                  textAlign="left"
                  fontSize="13px"
                  fontFamily="clash grotesk"
                >
                  Step 1 out of 3
                </Text>
                <Heading
                  fontWeight={500}
                  fontFamily="clash grotesk"
                  fontSize="30px"
                >
                  Create account
                </Heading>
              </Box>
              <FormControl fontFamily="clash grotesk">
                <FormLabel color="#808080">Username</FormLabel>
                <Input
                  type="text"
                  color="white"
                  borderColor="#808080"
                  borderRadius="12px"
                  placeholder="E.g Dezfoods"
                  fontFamily="clash grotesk"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                />

                {/* Display username error */}
              </FormControl>
              <FormControl fontFamily="clash grotesk">
                <FormLabel color="#808080">Email Address</FormLabel>
                <Input
                  type="email"
                  borderColor="#808080"
                  borderRadius="12px"
                  placeholder="Enter your email address"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
                {/* Display email error */}
              </FormControl>
              <FormControl fontFamily="clash grotesk">
                <FormLabel color="#808080">Password</FormLabel>
                <InputGroup>
                  <Input
                    type={showPassword1 ? "text" : "password"}
                    borderColor="#808080"
                    borderRadius="12px"
                    placeholder="Enter your password"
                    value={password1}
                    onChange={(e) => setPassword1(e.target.value)}
                  />
                  <InputRightElement width="4.5rem">
                    <Button
                      h="1.75rem"
                      bg="inherit"
                      size="sm"
                      _hover={{ bg: "inherit" }}
                      _active={{ bg: "inherit" }}
                      _focus={{ boxShadow: "none" }}
                      onClick={handleTogglePassword1}
                    >
                      {showPassword1 ? <ViewOffIcon /> : <ViewIcon />}
                    </Button>
                  </InputRightElement>
                </InputGroup>
                {/* Display password error */}
              </FormControl>
              <FormControl fontFamily="clash grotesk">
                <FormLabel color="#808080">Confirm Password</FormLabel>
                <InputGroup>
                  <Input
                    type={showPassword2 ? "text" : "password"}
                    borderColor="#808080"
                    borderRadius="12px"
                    placeholder="Confirm your password"
                    value={password2}
                    onChange={(e) => setPassword2(e.target.value)}
                  />
                  <InputRightElement width="4.5rem">
                    <Button
                      h="1.75rem"
                      bg="inherit"
                      _hover={{ bg: "inherit" }}
                      _active={{ bg: "inherit" }}
                      _focus={{ boxShadow: "none" }}
                      size="sm"
                      onClick={handleTogglePassword2}
                    >
                      {showPassword2 ? <ViewOffIcon /> : <ViewIcon />}
                    </Button>
                  </InputRightElement>
                </InputGroup>
                {/* Display password error */}
              </FormControl>
            </VStack>
          </Flex>
        );

      //Second registration step. Gender, country and states
      case 2:
        return (
          <Flex
            color="white"
            bg="black"
            alignItems="center"
            justifyContent="center"
            mt="40px"
            fontFamily="clash grotesk"
          >
            <VStack spacing={6} width={{ base: "80%", md: "500px" }}>
              <Box>
                <Text textAlign="left" fontSize="13px">
                  Step 2 out of 3
                </Text>
                <Heading
                  fontWeight={500}
                  fontSize="30px"
                  fontFamily="clash grotesk"
                >
                  Create account
                </Heading>
              </Box>

              <FormControl>
                <FormLabel color="#808080">Gender</FormLabel>
                <Select value={selectedGender} onChange={handleGenderChange}>
                  <option value="">Select Gender</option>
                  <option value="male" style={dropdownOptionStyles}>
                    Male
                  </option>
                  <option value="female" style={dropdownOptionStyles}>
                    Female
                  </option>
                  {/* Add more gender options as needed */}
                </Select>
                {genderError && <Text color="#CB29BE">{genderError}</Text>}
              </FormControl>
              <FormControl fontFamily="clash grotesk">
                <FormLabel>Country:</FormLabel>
                <Select
                  borderColor="#808080"
                  borderRadius="12px"
                  value={selectedCountry}
                  onChange={handleCountryChange}
                >
                  <option value="">Select Country</option>
                  {countries.map((country) => (
                    <option
                      key={country}
                      value={country}
                      style={dropdownOptionStyles}
                    >
                      {country}
                    </option>
                  ))}
                </Select>
                {countryError && <Text color="#CB29BE">{countryError}</Text>}
              </FormControl>

              <FormControl>
                <FormLabel>State:</FormLabel>
                <Select
                  borderColor="#808080"
                  borderRadius="12px"
                  value={selectedState}
                  onChange={handleStateChange}
                >
                  {stateLoad ? (
                    <option value="">Loading States...</option>
                  ) : (
                    states.map((state) => (
                      <option
                        key={state}
                        value={state}
                        style={dropdownOptionStyles}
                      >
                        {state}
                      </option>
                    ))
                  )}
                </Select>
                {stateError && <Text color="#CB29BE">{stateError}</Text>}
              </FormControl>

              <FormControl>
                <FormLabel color="#808080">Local Government Area</FormLabel>
                <Select
                  borderColor="#808080"
                  borderRadius="12px"
                  value={selectedCity}
                  onChange={handleCityChange}
                >
                  {localLoad ? (
                    <option value="">Loading Cities...</option>
                  ) : (
                    cities.map((city) => (
                      <option
                        key={city}
                        value={city}
                        style={dropdownOptionStyles}
                      >
                        {city}
                      </option>
                    ))
                  )}
                </Select>
                <Text color="#808080" fontSize="14px">
                  This helps us match you with vendors close to your market
                  place
                </Text>
                {cityError && <Text color="#CB29BE">{cityError}</Text>}
              </FormControl>
            </VStack>
          </Flex>
        );

      //Third registration step. Verification of email
      case 3:
        return (
          <Flex justify={"center"}>
            <Stack
              spacing={4}
              w={"full"}
              maxW={"sm"}
              rounded={"xl"}
              boxShadow={"lg"}
              p={6}
              my={10}
              fontFamily="clash grotesk"
            >
              <Box color="white" textAlign="center" fontFamily="clash grotesk">
                <Text fontSize="13px" textAlign="center">
                  Step 3 out of 3
                </Text>
                <Heading
                  lineHeight={1.1}
                  fontSize="20px"
                  fontWeight="500"
                  fontFamily="clash grotesk"
                >
                  Verify your email address
                </Heading>
              </Box>

              <FormControl>
                <Text
                  textAlign="center"
                  color="#808080"
                  fontFamily="clash grotesk"
                  mb={8}
                >
                  We've sent an email with your account activation code to
                  <span style={{ color: "#CB29BE" }}> {email}</span>
                </Text>
                <Center>
                  <HStack spacing={2}>
                    {[0, 1, 2, 3, 4, 5].map((index) => (
                      <Input
                        key={index}
                        type="number"
                        id={`pin${index}`}
                        value={pin[index]}
                        onChange={(e) => handlePinChange(e, index)}
                        maxLength={1} // Allow only one digit per input
                        borderColor="#808080"
                        borderRadius="12px"
                        width={{ base: "45px", md: "60px" }}
                        height={{ base: "45px", md: "60px" }}
                        textAlign="center"
                        color="white"
                        autoFocus={index === 0} // Autofocus on the first input
                      />
                    ))}
                  </HStack>
                </Center>
                <Text
                  textAlign="center"
                  color="white"
                  fontFamily="clash grotesk"
                  mt={5}
                >
                  Didn't receive a code ?{" "}
                  <Button
                    variant="unstyled"
                    style={{ color: "#CB29BE" }}
                    onClick={handleResendClick}
                    isDisabled={codeLoad && true}
                    fontWeight="400"
                  >
                    {codeLoad ? <Spinner size="sm" color="white" /> : "Resend"}
                  </Button>
                </Text>
              </FormControl>

              {resendSuccess && (
                <Text color="#cb29be">
                  New code sent to your email. Please Check
                </Text>
              )}

              {error && (
                <Text textAlign="center" color="#CB29BE">
                  {error}
                </Text>
              )}
            </Stack>
          </Flex>
        );

      case 4:
        // Fourth step (dummy text)
        return (
          <Box
            color="white"
            bg="black"
            textAlign="center"
            mx="auto"
            mt="100"
            height="100vh"
            fontFamily="clash grotesk"
            width={{ base: "80%", md: "500px" }}
          >
            <iconify-icon
              icon="solar:verified-check-bold"
              style={{ color: "#CB29BE" }}
              width="120"
            ></iconify-icon>
            <Heading
              textAlign="center"
              fontFamily="clash grotesk"
              fontWeight="500"
            >
              Account verified
            </Heading>
            <Text fontSize="sm" color="#808080" textAlign="center" mt={2}>
              Your account has been verified successfully
            </Text>
            <Center>
              <Button
                bg="#CB29BE"
                color="white"
                fontWeight={500}
                rounded="25px"
                px={10}
                width={{ base: "80%", md: "500px" }}
                mt={8}
                mb={2}
                _hover={{ bg: "#CB29BE", opacity: "0.9" }}
                fontFamily="clash grotesk"
                display="flex"
                justifyContent="center"
                as={Link}
                to="/log-in"
              >
                Go to profile <ArrowForwardIcon ml={3} />
              </Button>
            </Center>
          </Box>
        );

      default:
        return;
    }
  };

  const [showPassword1, setShowPassword1] = useState(false);
  const [showPassword2, setShowPassword2] = useState(false);

  const handleTogglePassword1 = () => {
    setShowPassword1(!showPassword1);
  };

  const handleTogglePassword2 = () => {
    setShowPassword2(!showPassword2);
  };

  return (
    <Container maxWidth="100vw" bg="black" px={0} pt="14">
      <Grid
        templateColumns={{ base: "1fr", md: "2.3fr 7.7fr" }}
        fontFamily="clash grotesk"
      >
        <Image
          src={Onboard}
          alt="Onboarding_pics"
          objectFit="cover"
          display={{ base: "none", md: "flex" }}
          height="full"
        />
        <Box mt={{ base: "5", md: "20" }}>
          {renderStepContent()}
          <Box
            display="flex"
            justifyContent="center"
            fontFamily="clash grotesk"
          >
            {currentStep > 1 && currentStep < 4 && (
              <ArrowBackIcon
                color="white"
                fontSize="30px"
                position="absolute"
                left={{ base: "10px", md: "30%" }}
                top={{ base: "80px", md: "120px" }}
                cursor="pointer"
                onClick={handlePreviousStep}
              />
            )}

            {currentStep < 3 && (
              <Button
                onClick={handleNextStep}
                bg="#CB29BE"
                color="white"
                fontWeight={500}
                rounded="25px"
                px={10}
                width={{ base: "80%", md: "500px" }}
                mt={8}
                mb={2}
                _hover={{ bg: "#CB29BE", opacity: "0.9" }}
                fontFamily="clash grotesk"
              >
                {isLoading ? (
                  <>
                    <Loader />
                    sending code....
                  </>
                ) : (
                  "Proceed"
                )}
              </Button>
            )}

            {currentStep === 3 && (
              <Button
                bg="#CB29BE"
                color="white"
                fontWeight={500}
                rounded="25px"
                px={10}
                width={{ base: "80%", md: "500px" }}
                _hover={{ bg: "#CB29BE", opacity: "0.9" }}
                fontFamily="clash grotesk"
                onClick={handleVerifyEmail}
                isDisabled={!isPinFilled()}
                mb={{ base: "300px", md: "0" }}
              >
                {mailLoading ? (
                  <>
                    <Loader />
                    Authenticating code....
                  </>
                ) : (
                  "Verify & create account"
                )}
              </Button>
            )}
          </Box>
          {currentStep < 3 && (
            <Text
              textAlign="center"
              color="white"
              fontFamily="clash grotesk"
              mb={40}
            >
              Already have an account ?{" "}
              <Button
                variant="unstyled"
                style={{ color: "#CB29BE" }}
                as={Link}
                to="/log-in"
                fontWeight="400"
              >
                {" "}
                Log in{" "}
              </Button>
            </Text>
          )}
        </Box>
      </Grid>
    </Container>
  );
}

export default SignUpComponent;
