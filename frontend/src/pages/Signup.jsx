import { Box, Card, TextField, Button, Typography } from "@mui/material";
import { useNavigate } from "react-router-dom";
import Logo from "../assets/logo.svg";

function Signup() {
    const navigate = useNavigate();
    return (
        <Card
            sx={{
                width: 380,
                padding: 7,
                borderRadius: 3,
                backgroundColor: "#ffffff",
                boxShadow: "0px 10px 40px rgba(0,0,0,0.3)",
                textAlign: "center"
            }}>

            {/* Title */}
            <Box display="flex" alignItems="center" flexDirection="column" mb={2}>
                <img src={Logo} alt="Secure Drive logo" style={{ width: 150, height: 150, marginBottom: 6 }} />
                <Typography variant="h3" fontWeight={700} lineHeight={1.1} sx={{ fontSize: "1.8rem" }}>
                    Secure Drive
                </Typography>
            </Box>
            <Box display="flex" alignItems="center" flexDirection="column" mb={2}>
                <Typography variant="h3" fontWeight={700} lineHeight={1.1} sx={{ fontSize: "1.3rem" }}>
                    Create Account
                </Typography>
            </Box>

            {/* Email */}
            <Box mb={2} textAlign="left">
                <Typography variant="body2" mb={0.5}>
                    Email
                </Typography>
                <TextField fullWidth size="small" placeholder="Enter your email" />
            </Box>

            {/* Password */}
            <Box mb={2} textAlign="left">
                <Typography variant="body2" mb={0.5}>
                    Password
                </Typography>
                <TextField fullWidth size="small" type="password" placeholder="Create a password" />
            </Box>

            {/* Confirm Password */}
            <Box mb={3} textAlign="left">
                <Typography variant="body2" mb={0.5}>
                    Confirm Password
                </Typography>
                <TextField fullWidth size="small" type="password" placeholder="Confirm your password" />
            </Box>

            {/* Signup button */}
            <Button fullWidth variant="contained"
                sx={{
                    backgroundColor: "#4F46E5",
                    borderRadius: 2,
                    textTransform: "none",
                    fontWeight: 500,
                    py: 1,
                    mb: 2
                }}>
                Sign Up
            </Button>

            {/* Switch to login */}
            <Typography variant="body2">
                Already have an account?{" "}
                <span style={{ color: "#4F46E5", cursor: "pointer" }} onClick={() => navigate("/login")}>
                    Login
                </span>
            </Typography>
        </Card>
    );
}

export default Signup;
