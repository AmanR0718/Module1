import React from 'react';
import { View, Text, TextInput, StyleSheet } from 'react-native';

const FormInput = ({
    label,
    value,
    onChangeText,
    placeholder,
    error,
    touched,
    keyboardType = 'default',
    secureTextEntry = false,
    multiline = false,
    numberOfLines = 1,
    editable = true,
}) => {
    return (
        <View style={styles.container}>
            {label && <Text style={styles.label}>{label}</Text>}
            <TextInput
                style={[
                    styles.input,
                    multiline && styles.multilineInput,
                    error && touched && styles.inputError,
                    !editable && styles.inputDisabled,
                ]}
                value={value}
                onChangeText={onChangeText}
                placeholder={placeholder}
                keyboardType={keyboardType}
                secureTextEntry={secureTextEntry}
                multiline={multiline}
                numberOfLines={numberOfLines}
                editable={editable}
            />
            {error && touched && <Text style={styles.errorText}>{error}</Text>}
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        marginBottom: 15,
    },
    label: {
        fontSize: 14,
        fontWeight: '600',
        color: '#333',
        marginBottom: 5,
    },
    input: {
        backgroundColor: '#fff',
        borderWidth: 1,
        borderColor: '#ddd',
        borderRadius: 5,
        padding: 12,
        fontSize: 16,
    },
    multilineInput: {
        minHeight: 80,
        textAlignVertical: 'top',
    },
    inputError: {
        borderColor: '#FF5252',
    },
    inputDisabled: {
        backgroundColor: '#f5f5f5',
        color: '#999',
    },
    errorText: {
        color: '#FF5252',
        fontSize: 12,
        marginTop: 5,
    },
});

export default FormInput;