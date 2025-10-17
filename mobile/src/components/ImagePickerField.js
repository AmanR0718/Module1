import React, { useState } from 'react';
import {
    View,
    Text,
    Image,
    TouchableOpacity,
    StyleSheet,
    Alert,
    ActivityIndicator,
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { Ionicons } from '@expo/vector-icons';

const ImagePickerField = ({
    label = 'Upload Image',
    onImagePicked,
    initialImage = null,
    mode = 'photo', // 'photo' or 'id'
}) => {
    const [image, setImage] = useState(initialImage);
    const [loading, setLoading] = useState(false);

    // ============================================================
    // 🔹 REQUEST CAMERA PERMISSION
    // ============================================================
    const requestPermission = async () => {
        const { status } = await ImagePicker.requestCameraPermissionsAsync();
        if (status !== 'granted') {
            Alert.alert('Permission Denied', 'Camera access is required to take photos.');
            return false;
        }
        return true;
    };

    // ============================================================
    // 🔹 PICK IMAGE (from camera or gallery)
    // ============================================================
    const handlePickImage = async () => {
        try {
            const permissionGranted = await requestPermission();
            if (!permissionGranted) return;

            Alert.alert(
                'Select Option',
                'Choose how to add the image',
                [
                    {
                        text: '📸 Take Photo',
                        onPress: async () => await launchCamera(),
                    },
                    {
                        text: '🖼️ Choose from Gallery',
                        onPress: async () => await launchGallery(),
                    },
                    { text: 'Cancel', style: 'cancel' },
                ],
                { cancelable: true }
            );
        } catch (error) {
            console.error('Error picking image:', error);
        }
    };

    const launchCamera = async () => {
        const result = await ImagePicker.launchCameraAsync({
            allowsEditing: true,
            aspect: [4, 4],
            quality: 0.7,
        });

        if (!result.canceled) {
            const uri = result.assets[0].uri;
            setImage(uri);
            onImagePicked && onImagePicked(uri);
        }
    };

    const launchGallery = async () => {
        const result = await ImagePicker.launchImageLibraryAsync({
            allowsEditing: true,
            aspect: [4, 4],
            quality: 0.8,
        });

        if (!result.canceled) {
            const uri = result.assets[0].uri;
            setImage(uri);
            onImagePicked && onImagePicked(uri);
        }
    };

    // ============================================================
    // 🔹 REMOVE IMAGE
    // ============================================================
    const handleRemoveImage = () => {
        Alert.alert('Remove Image', 'Do you want to remove this image?', [
            { text: 'Cancel', style: 'cancel' },
            {
                text: 'Remove',
                onPress: () => {
                    setImage(null);
                    onImagePicked && onImagePicked(null);
                },
                style: 'destructive',
            },
        ]);
    };

    // ============================================================
    // 🔹 RENDER
    // ============================================================
    return (
        <View style={styles.container}>
            {label && <Text style={styles.label}>{label}</Text>}

            <TouchableOpacity
                style={styles.uploadBox}
                onPress={handlePickImage}
                disabled={loading}
            >
                {loading ? (
                    <ActivityIndicator color="#198A48" />
                ) : image ? (
                    <>
                        <Image source={{ uri: image }} style={styles.previewImage} />
                        <TouchableOpacity style={styles.removeButton} onPress={handleRemoveImage}>
                            <Ionicons name="close-circle" size={22} color="#E74C3C" />
                        </TouchableOpacity>
                    </>
                ) : (
                    <View style={styles.placeholder}>
                        <Ionicons
                            name={mode === 'id' ? 'card-outline' : 'camera-outline'}
                            size={32}
                            color="#198A48"
                        />
                        <Text style={styles.placeholderText}>
                            {mode === 'id' ? 'Upload ID Document' : 'Take Farmer Photo'}
                        </Text>
                    </View>
                )}
            </TouchableOpacity>
        </View>
    );
};

// ============================================================
// 🔹 STYLES
// ============================================================
const styles = StyleSheet.create({
    container: {
        marginBottom: 20,
    },
    label: {
        fontSize: 14,
        fontWeight: '600',
        color: '#333',
        marginBottom: 8,
    },
    uploadBox: {
        backgroundColor: '#fff',
        borderWidth: 1,
        borderColor: '#ddd',
        borderRadius: 10,
        justifyContent: 'center',
        alignItems: 'center',
        height: 180,
        position: 'relative',
    },
    placeholder: {
        alignItems: 'center',
        justifyContent: 'center',
    },
    placeholderText: {
        color: '#7f8c8d',
        fontSize: 14,
        marginTop: 6,
    },
    previewImage: {
        width: '100%',
        height: '100%',
        borderRadius: 10,
    },
    removeButton: {
        position: 'absolute',
        top: 8,
        right: 8,
        backgroundColor: 'rgba(255,255,255,0.8)',
        borderRadius: 20,
        padding: 2,
    },
});

export default ImagePickerField;
