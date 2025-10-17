import React, { useState } from "react";
import {
    View,
    Text,
    TextInput,
    TouchableOpacity,
    StyleSheet,
    Alert,
    ActivityIndicator,
    KeyboardAvoidingView,
    Platform,
    ScrollView,
} from "react-native";
import { resetPassword } from "../services/api";

const ResetPasswordScreen = ({ navigation, route }) => {
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState(false);

    // Extract token from route params (passed from email or link)
    const token = route?.params?.token || "";

    // ============================================================
    // 🔹 HANDLE PASSWORD RESET
    // ============================================================
    const handleResetPassword = async () => {
        if (!password || !confirmPassword) {
            Alert.alert("Error", "Please fill out all fields");
            return;
        }

        if (password.length < 6) {
            Alert.alert("Error", "Password must be at least 6 characters long");
            return;
        }

        if (password !== confirmPassword) {
            Alert.alert("Error", "Passwords do not match");
            return;
        }

        if (!token) {
            Alert.alert("Error", "Invalid or missing reset token");
            return;
        }

        setLoading(true);
        try {
            await resetPassword(token, password);
            setSuccess(true);
            Alert.alert("Success", "Password reset successfully!");
            navigation.replace("Login");
        } catch (error) {
            Alert.alert(
                "Failed",
                error.response?.data?.detail || "Unable to reset password"
            );
        } finally {
            setLoading(false);
        }
    };

    return (
        <KeyboardAvoidingView
            style={styles.container}
            behavior={Platform.OS === "ios" ? "padding" : undefined}
        >
            <ScrollView
                contentContainerStyle={{ flexGrow: 1, justifyContent: "center" }}
                keyboardShouldPersistTaps="handled"
            >
                {/* Header */}
                <View style={styles.header}>
                    <Text style={styles.title}>Reset Password</Text>
                    <Text style={styles.subtitle}>Enter your new password below</Text>
                </View>

                {/* Form */}
                <View style={styles.form}>
                    <TextInput
                        style={styles.input}
                        placeholder="New Password"
                        secureTextEntry
                        value={password}
                        onChangeText={setPassword}
                        editable={!loading}
                    />

                    <TextInput
                        style={styles.input}
                        placeholder="Confirm Password"
                        secureTextEntry
                        value={confirmPassword}
                        onChangeText={setConfirmPassword}
                        editable={!loading}
                    />

                    <TouchableOpacity
                        style={[styles.button, loading && styles.buttonDisabled]}
                        onPress={handleResetPassword}
                        disabled={loading}
                    >
                        {loading ? (
                            <ActivityIndicator color="#fff" />
                        ) : (
                            <Text style={styles.buttonText}>Reset Password</Text>
                        )}
                    </TouchableOpacity>

                    {success && (
                        <Text style={styles.successText}>
                            ✅ Password successfully reset. Please log in again.
                        </Text>
                    )}

                    <TouchableOpacity onPress={() => navigation.navigate("Login")}>
                        <Text style={styles.backText}>⬅ Back to Login</Text>
                    </TouchableOpacity>
                </View>
            </ScrollView>
        </KeyboardAvoidingView>
    );
};

// ============================================================
// 🔹 STYLES
// ============================================================
const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: "#198A48",
        justifyContent: "center",
        padding: 20,
    },
    header: {
        alignItems: "center",
        marginBottom: 40,
    },
    title: {
        fontSize: 28,
        fontWeight: "bold",
        color: "#fff",
    },
    subtitle: {
        fontSize: 16,
        color: "#fff",
        marginTop: 5,
        textAlign: "center",
    },
    form: {
        backgroundColor: "#fff",
        borderRadius: 10,
        padding: 25,
    },
    input: {
        borderWidth: 1,
        borderColor: "#ddd",
        borderRadius: 8,
        padding: 15,
        marginBottom: 15,
        fontSize: 16,
    },
    button: {
        backgroundColor: "#198A48",
        borderRadius: 8,
        paddingVertical: 15,
        alignItems: "center",
        marginTop: 10,
    },
    buttonDisabled: {
        opacity: 0.6,
    },
    buttonText: {
        color: "#fff",
        fontSize: 16,
        fontWeight: "bold",
    },
    successText: {
        color: "#27ae60",
        textAlign: "center",
        marginTop: 15,
        fontWeight: "600",
    },
    backText: {
        color: "#198A48",
        textAlign: "center",
        marginTop: 20,
        fontWeight: "600",
    },
});

export default ResetPasswordScreen;
