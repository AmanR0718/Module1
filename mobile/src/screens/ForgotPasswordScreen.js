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
import { forgotPassword } from "../services/api";

const ForgotPasswordScreen = ({ navigation }) => {
    const [email, setEmail] = useState("");
    const [loading, setLoading] = useState(false);
    const [sent, setSent] = useState(false);

    // ============================================================
    // 🔹 HANDLE PASSWORD RESET REQUEST
    // ============================================================
    const handleForgotPassword = async () => {
        if (!email) {
            Alert.alert("Error", "Please enter your registered email");
            return;
        }

        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
            Alert.alert("Error", "Please enter a valid email address");
            return;
        }

        setLoading(true);
        try {
            const data = await forgotPassword(email);
            setSent(true);
            Alert.alert("Success", "Password reset link sent to your email (mock).");
            console.log("🔗 Reset link:", data.reset_link);
        } catch (error) {
            Alert.alert(
                "Failed",
                error.response?.data?.detail || "Unable to send reset link"
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
                    <Text style={styles.title}>Forgot Password</Text>
                    <Text style={styles.subtitle}>
                        Enter your registered email address
                    </Text>
                </View>

                {/* Form */}
                <View style={styles.form}>
                    <TextInput
                        style={styles.input}
                        placeholder="Email"
                        value={email}
                        onChangeText={setEmail}
                        autoCapitalize="none"
                        keyboardType="email-address"
                        editable={!loading}
                    />

                    <TouchableOpacity
                        style={[styles.button, loading && styles.buttonDisabled]}
                        onPress={handleForgotPassword}
                        disabled={loading}
                    >
                        {loading ? (
                            <ActivityIndicator color="#fff" />
                        ) : (
                            <Text style={styles.buttonText}>Send Reset Link</Text>
                        )}
                    </TouchableOpacity>

                    {sent && (
                        <Text style={styles.successText}>
                            ✅ Reset link sent. Please check your email.
                        </Text>
                    )}

                    <TouchableOpacity onPress={() => navigation.goBack()}>
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

export default ForgotPasswordScreen;
