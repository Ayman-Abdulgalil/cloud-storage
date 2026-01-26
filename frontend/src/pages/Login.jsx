import { Box, Card, TextField, Button, Typography } from "@mui/material";
import { useNavigate } from "react-router-dom";
import Logo from "../assets/logo.svg";


function Login() {
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

            <Typography variant="h3" fontWeight={700} lineHeight={1.1} sx={{ whiteSpace: "nowrap", fontSize: "1.8rem" }}>
                Secure Drive
            </Typography>
        </Box>
        <Box display="flex" alignItems="center" flexDirection="column" mb={2}>

            <Typography variant="h3" fontWeight={700} lineHeight={1.1} sx={{ whiteSpace: "nowrap", fontSize: "1.3rem" }}>
                Login
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
            <TextField fullWidth size="small" type="password" placeholder="Enter your password" />
        </Box>

        {/* Forgot password */}
        <Typography variant="body2" sx={{ 
            textAlign: "right", 
            mb: 2, 
            cursor: "pointer" }}>
                Forgot password?
        </Typography>

        {/* Login button */}
        <Button fullWidth variant="contained" onClick={() => navigate("/dashboard")}
            sx={{
                backgroundColor: "#4F46E5", 
                borderRadius: 2, 
                textTransform: "none", 
                fontWeight: 500, 
                py: 1, mb: 2}}>
                Login
        </Button>
        <Typography variant="body2">
                Don't have an account?{" "}
            <span style={{ color: "#4F46E5", cursor: "pointer" }} onClick={() => navigate("/signup")}>
                Sign up
            </span>
        </Typography>
        {/* Signup link */}
        </Card>
    );
}

export default Login;
