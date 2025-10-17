import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Alert, ScrollView } from 'react-native';
import { Formik } from 'formik';
import { personalInfoSchema, addressSchema, landParcelSchema, cropSchema } from '../utils/validation';
import FormInput from './FormInput';
import { insertFarmer, insertLandParcel, insertCrop } from '../services/database';
import { v4 as uuidv4 } from 'uuid';
import { getCurrentLocation } from '../utils/location';

const steps = ['Personal Info', 'Address', 'Land', 'Crops', 'Review'];

const FormWizard = ({ navigation }) => {
    const [step, setStep] = useState(0);
    const [formValues, setFormValues] = useState({
        personal_info: {},
        address: {},
        land_parcel: {},
        crop: {},
    });

    const nextStep = () => {
        if (step < steps.length - 1) setStep(step + 1);
    };

    const prevStep = () => {
        if (step > 0) setStep(step - 1);
    };

    // ------------------------------------------------------
    // 🔹 SAVE OFFLINE
    // ------------------------------------------------------
    const handleSaveOffline = async () => {
        try {
            const temp_id = uuidv4();
            const { latitude, longitude } = await getCurrentLocation();

            const farmerData = {
                ...formValues.personal_info,
                ...formValues.address,
                latitude,
                longitude,
                temp_id,
                sync_status: 'pending',
            };

            const farmerId = await insertFarmer(farmerData);
            await insertLandParcel(temp_id, formValues.land_parcel);
            await insertCrop(temp_id, formValues.crop);

            Alert.alert('✅ Success', 'Farmer saved offline for sync.');
            navigation.goBack();
        } catch (error) {
            console.error('Error saving farmer:', error);
            Alert.alert('❌ Error', 'Failed to save farmer data');
        }
    };

    // ------------------------------------------------------
    // 🔹 RENDER STEP COMPONENT
    // ------------------------------------------------------
    const renderStep = (formik) => {
        switch (step) {
            case 0:
                return (
                    <>
                        <Text style={styles.stepTitle}>👤 Personal Information</Text>
                        <FormInput label="First Name" value={formik.values.first_name} onChangeText={formik.handleChange('first_name')} error={formik.errors.first_name} touched={formik.touched.first_name} />
                        <FormInput label="Last Name" value={formik.values.last_name} onChangeText={formik.handleChange('last_name')} error={formik.errors.last_name} touched={formik.touched.last_name} />
                        <FormInput label="Phone Number (+260...)" value={formik.values.phone_primary} onChangeText={formik.handleChange('phone_primary')} keyboardType="phone-pad" error={formik.errors.phone_primary} touched={formik.touched.phone_primary} />
                        <FormInput label="NRC Number" value={formik.values.nrc_number} onChangeText={formik.handleChange('nrc_number')} error={formik.errors.nrc_number} touched={formik.touched.nrc_number} />
                        <FormInput label="Gender (male/female)" value={formik.values.gender} onChangeText={formik.handleChange('gender')} error={formik.errors.gender} touched={formik.touched.gender} />
                    </>
                );
            case 1:
                return (
                    <>
                        <Text style={styles.stepTitle}>📍 Address Details</Text>
                        <FormInput label="Province" value={formik.values.province} onChangeText={formik.handleChange('province')} error={formik.errors.province} touched={formik.touched.province} />
                        <FormInput label="District" value={formik.values.district} onChangeText={formik.handleChange('district')} error={formik.errors.district} touched={formik.touched.district} />
                        <FormInput label="Village" value={formik.values.village} onChangeText={formik.handleChange('village')} error={formik.errors.village} touched={formik.touched.village} />
                        <FormInput label="Chiefdom" value={formik.values.chiefdom} onChangeText={formik.handleChange('chiefdom')} error={formik.errors.chiefdom} touched={formik.touched.chiefdom} />
                    </>
                );
            case 2:
                return (
                    <>
                        <Text style={styles.stepTitle}>🌾 Land Parcel</Text>
                        <FormInput label="Total Area (hectares)" value={formik.values.total_area} onChangeText={formik.handleChange('total_area')} keyboardType="decimal-pad" error={formik.errors.total_area} touched={formik.touched.total_area} />
                        <FormInput label="Ownership Type (owned/leased/shared)" value={formik.values.ownership_type} onChangeText={formik.handleChange('ownership_type')} error={formik.errors.ownership_type} touched={formik.touched.ownership_type} />
                        <FormInput label="Land Type (irrigated/non_irrigated)" value={formik.values.land_type} onChangeText={formik.handleChange('land_type')} error={formik.errors.land_type} touched={formik.touched.land_type} />
                        <FormInput label="Soil Type" value={formik.values.soil_type} onChangeText={formik.handleChange('soil_type')} />
                    </>
                );
            case 3:
                return (
                    <>
                        <Text style={styles.stepTitle}>🌱 Crop Details</Text>
                        <FormInput label="Crop Name" value={formik.values.crop_name} onChangeText={formik.handleChange('crop_name')} error={formik.errors.crop_name} touched={formik.touched.crop_name} />
                        <FormInput label="Variety" value={formik.values.variety} onChangeText={formik.handleChange('variety')} />
                        <FormInput label="Area Allocated (hectares)" value={formik.values.area_allocated} onChangeText={formik.handleChange('area_allocated')} keyboardType="decimal-pad" error={formik.errors.area_allocated} touched={formik.touched.area_allocated} />
                        <FormInput label="Season" value={formik.values.season} onChangeText={formik.handleChange('season')} error={formik.errors.season} touched={formik.touched.season} />
                    </>
                );
            case 4:
                return (
                    <View style={styles.reviewBox}>
                        <Text style={styles.reviewText}>✅ Review all entered details and save offline.</Text>
                    </View>
                );
            default:
                return null;
        }
    };

    // ------------------------------------------------------
    // 🔹 VALIDATION PER STEP
    // ------------------------------------------------------
    const getValidationSchema = () => {
        switch (step) {
            case 0:
                return personalInfoSchema;
            case 1:
                return addressSchema;
            case 2:
                return landParcelSchema;
            case 3:
                return cropSchema;
            default:
                return null;
        }
    };

    // ------------------------------------------------------
    // 🔹 INITIAL VALUES PER STEP
    // ------------------------------------------------------
    const getInitialValues = () => {
        switch (step) {
            case 0:
                return formValues.personal_info;
            case 1:
                return formValues.address;
            case 2:
                return formValues.land_parcel;
            case 3:
                return formValues.crop;
            default:
                return {};
        }
    };

    // ------------------------------------------------------
    // 🔹 FORM SUBMISSION
    // ------------------------------------------------------
    const handleFormSubmit = (values) => {
        const updatedValues = { ...formValues };
        if (step === 0) updatedValues.personal_info = values;
        if (step === 1) updatedValues.address = values;
        if (step === 2) updatedValues.land_parcel = values;
        if (step === 3) updatedValues.crop = values;
        setFormValues(updatedValues);

        if (step === steps.length - 1) {
            handleSaveOffline();
        } else {
            nextStep();
        }
    };

    return (
        <ScrollView contentContainerStyle={styles.container}>
            <Text style={styles.header}>Farmer Registration Wizard</Text>
            <Text style={styles.progressText}>Step {step + 1} of {steps.length} — {steps[step]}</Text>

            <Formik
                initialValues={getInitialValues()}
                validationSchema={getValidationSchema()}
                enableReinitialize
                onSubmit={handleFormSubmit}
            >
                {(formik) => (
                    <>
                        {renderStep(formik)}

                        <View style={styles.navButtons}>
                            {step > 0 && (
                                <TouchableOpacity style={[styles.button, styles.backBtn]} onPress={prevStep}>
                                    <Text style={styles.buttonText}>⬅ Back</Text>
                                </TouchableOpacity>
                            )}

                            <TouchableOpacity style={[styles.button, styles.nextBtn]} onPress={formik.handleSubmit}>
                                <Text style={styles.buttonText}>{step === steps.length - 1 ? '💾 Save Offline' : 'Next ➡'}</Text>
                            </TouchableOpacity>
                        </View>
                    </>
                )}
            </Formik>
        </ScrollView>
    );
};

const styles = StyleSheet.create({
    container: {
        padding: 20,
        backgroundColor: '#f8f9fa',
    },
    header: {
        fontSize: 22,
        fontWeight: 'bold',
        color: '#198A48',
        textAlign: 'center',
        marginBottom: 10,
    },
    stepTitle: {
        fontSize: 18,
        fontWeight: '600',
        color: '#2c3e50',
        marginBottom: 10,
    },
    progressText: {
        textAlign: 'center',
        color: '#7f8c8d',
        marginBottom: 20,
    },
    navButtons: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        marginTop: 20,
    },
    button: {
        flex: 1,
        padding: 15,
        borderRadius: 8,
        alignItems: 'center',
        marginHorizontal: 5,
    },
    nextBtn: {
        backgroundColor: '#198A48',
    },
    backBtn: {
        backgroundColor: '#95a5a6',
    },
    buttonText: {
        color: '#fff',
        fontWeight: 'bold',
    },
    reviewBox: {
        padding: 20,
        backgroundColor: '#fff',
        borderRadius: 10,
        elevation: 2,
        marginTop: 20,
    },
    reviewText: {
        fontSize: 16,
        color: '#2c3e50',
        textAlign: 'center',
    },
});

export default FormWizard;
