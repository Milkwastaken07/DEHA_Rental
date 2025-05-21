
from apps.models import Tenant
import logging
from django.db import IntegrityError

def getTenant(cognitoId: str):
    try:
        tenant = Tenant.objects.filter(cognitoId = cognitoId, favorites__isnull=False)
        logging.info(f"Found Tenant: {tenant.name} (cognitoId: {cognitoId})")
        return tenant
    except Tenant.DoesNotExist:
        logging.warning(f"No Tenant found with cognitoId: {cognitoId} or no favorites")
        return None
    except Exception as e:
        logging.error(f"Error retrieving Tenant with cognitoId {cognitoId}: {e}")
        raise

def createTenant(cognitoId: str, name: str, email: str, phoneNumber: str):
    """
    Create a new Tenant with the given details and optionally add favorite Properties.
    Args:
        cognito_id (str): Unique Cognito ID.
        name (str): Tenant name.
        email (str): Tenant email.
        phone_number (str): Tenant phone number.
        property_ids (list, optional): List of Property IDs to add to favorites.
    Returns:
        Tenant: Created Tenant instance.
    Raises:
        IntegrityError: If cognito_id already exists.
        ValueError: If input data is invalid.
        Exception: For other unexpected errors.
    """
    try:
        # Validate inputs
        if not all([cognitoId, name, email, phoneNumber]):
            raise ValueError("All fiels (cognitoId, name, email, phoneNumber) are required")
        tenant = Tenant.objects.create(
            cognitoId=cognitoId, 
            name=name, 
            email=email, 
            phoneNumber=phoneNumber
        )
        logging.info(f"Created Tenant: {tenant}")
        return tenant
    except IntegrityError as e:
        logging.error(f"Failed to create Tenant with cognitoId {cognitoId}: Duplicate cognitoId")
        raise ValueError(f"Tenant with cognitoId {cognitoId} already exists")
    except ValueError as e:
        logging.error(f"Invalid input for creating Tenant: {str(e)}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error creating Tenant with cognitoId {cognitoId}: {str(e)}")
        raise

def updateTenant(cognitoId: str, name: str, email: str, phoneNumber: str):
    """
    Create a new Tenant with the given details and optionally add favorite Properties.
    Args:
        cognito_id (str): Unique Cognito ID.
        name (str): Tenant name.
        email (str): Tenant email.
        phone_number (str): Tenant phone number.
        property_ids (list, optional): List of Property IDs to add to favorites.
    Returns:
        Tenant: Created Tenant instance.
    Raises:
        IntegrityError: If cognito_id already exists.
        ValueError: If input data is invalid.
        Exception: For other unexpected errors.
    """
    try:
        # Validate inputs
        if not all([cognitoId, name, email, phoneNumber]):
            raise ValueError("All fiels (cognitoId, name, email, phoneNumber) are required")
        updateTenant = Tenant.objects.get(cognitoId=cognitoId)
        updateTenant.name=name, 
        updateTenant.email=email, 
        updateTenant.phoneNumber=phoneNumber
        updateTenant.save()
        logging.info(f"Updated Tenant: {updateTenant}")
        return updateTenant
    except ValueError as e:
        logging.error(f"Invalid input for updating Tenant: {str(e)}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error updating Tenant with cognitoId {cognitoId}: {str(e)}")
        raise

    


    


