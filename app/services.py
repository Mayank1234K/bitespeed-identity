from sqlalchemy.orm import Session
from app.models import Contact
from datetime import datetime

def identify_contact(db: Session, email: str = None, phoneNumber: str = None):

    # Step 1: Find matching contacts
    query = db.query(Contact)

    if email and phoneNumber:
        existing = query.filter(
            (Contact.email == email) | (Contact.phoneNumber == phoneNumber)
        ).all()
    elif email:
        existing = query.filter(Contact.email == email).all()
    else:
        existing = query.filter(Contact.phoneNumber == phoneNumber).all()

    # Step 2: No existing contact → create new primary
    if not existing:
        new_contact = Contact(
            email=email,
            phoneNumber=phoneNumber,
            linkPrecedence="primary"
        )
        db.add(new_contact)
        db.commit()
        db.refresh(new_contact)

        return build_response([new_contact])

    # Step 3: Collect all related contacts
    primary_ids = set()

    for contact in existing:
        if contact.linkPrecedence == "primary":
            primary_ids.add(contact.id)
        else:
            primary_ids.add(contact.linkedId)

    all_related = db.query(Contact).filter(
        (Contact.id.in_(primary_ids)) |
        (Contact.linkedId.in_(primary_ids))
    ).all()

    # Step 4: Find oldest primary
    primary_contact = min(all_related, key=lambda x: x.createdAt)

    # Step 5: Convert other primaries to secondary
    for contact in all_related:
        if contact.linkPrecedence == "primary" and contact.id != primary_contact.id:
            contact.linkPrecedence = "secondary"
            contact.linkedId = primary_contact.id

    db.commit()

    # Step 6: Check for new information
    emails = {c.email for c in all_related if c.email}
    phones = {c.phoneNumber for c in all_related if c.phoneNumber}

    new_info = False

    if email and email not in emails:
        new_info = True
    if phoneNumber and phoneNumber not in phones:
        new_info = True

    if new_info:
        secondary = Contact(
            email=email,
            phoneNumber=phoneNumber,
            linkPrecedence="secondary",
            linkedId=primary_contact.id
        )
        db.add(secondary)
        db.commit()

        all_related.append(secondary)

    # Refresh final state
    final_contacts = db.query(Contact).filter(
        (Contact.id == primary_contact.id) |
        (Contact.linkedId == primary_contact.id)
    ).all()

    return build_response(final_contacts)


def build_response(contacts):
    primary = next(c for c in contacts if c.linkPrecedence == "primary")

    emails = list({c.email for c in contacts if c.email})
    phones = list({c.phoneNumber for c in contacts if c.phoneNumber})
    secondary_ids = [c.id for c in contacts if c.linkPrecedence == "secondary"]

    return {
        "contact": {
            "primaryContatctId": primary.id,
            "emails": emails,
            "phoneNumbers": phones,
            "secondaryContactIds": secondary_ids
        }
    }