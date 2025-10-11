import * as Yup from 'yup';

// Phone number validation (Zambian format)
export const phoneRegex = /^\+260-?\d{2}-?\d{7}$/;

// NRC validation
export const nrcRegex = /^\d{6}\/\d{2}\/\d{1}$/;

// Personal Info Schema
export const personalInfoSchema = Yup.object().shape({
    first_name: Yup.string()
        .min(2, 'Too short')
        .max(50, 'Too long')
        .required('First name is required'),
    last_name: Yup.string()
        .min(2, 'Too short')
        .max(50, 'Too long')
        .required('Last name is required'),
    phone_primary: Yup.string()
        .matches(phoneRegex, 'Invalid phone format. Use +260-XX-XXXXXXX')
        .required('Phone number is required'),
    phone_alternate: Yup.string()
        .matches(phoneRegex, 'Invalid phone format')
        .nullable(),
    email: Yup.string()
        .email('Invalid email')
        .nullable(),
    date_of_birth: Yup.date()
        .max(new Date(), 'Date cannot be in future')
        .required('Date of birth is required'),
    gender: Yup.string()
        .oneOf(['male', 'female', 'other'])
        .required('Gender is required'),
    nrc_number: Yup.string()
        .matches(nrcRegex, 'Invalid NRC format. Use XXXXXX/XX/X')
        .required('NRC number is required')
});

// Address Schema
export const addressSchema = Yup.object().shape({
    province: Yup.string().required('Province is required'),
    district: Yup.string().required('District is required'),
    village: Yup.string().required('Village is required'),
    chiefdom: Yup.string().nullable()
});

// Land Parcel Schema
export const landParcelSchema = Yup.object().shape({
    total_area: Yup.number()
        .min(0.1, 'Area must be at least 0.1 hectares')
        .max(1000, 'Area cannot exceed 1000 hectares')
        .required('Area is required'),
    ownership_type: Yup.string()
        .oneOf(['owned', 'leased', 'shared'])
        .required('Ownership type is required'),
    land_type: Yup.string()
        .oneOf(['irrigated', 'non_irrigated'])
        .required('Land type is required'),
    soil_type: Yup.string().nullable()
});

// Crop Schema
export const cropSchema = Yup.object().shape({
    crop_name: Yup.string().required('Crop name is required'),
    variety: Yup.string().nullable(),
    area_allocated: Yup.number()
        .min(0.1, 'Area must be at least 0.1 hectares')
        .required('Area is required'),
    planting_date: Yup.date().nullable(),
    expected_harvest_date: Yup.date().nullable(),
    irrigation_method: Yup.string().nullable(),
    estimated_yield: Yup.number().min(0).nullable(),
    season: Yup.string().required('Season is required')
});