# Copyright (c) 2026 Ville Heikkiniemi, Luka Hietala, Luukas Kola
#
# This code is licensed under the MIT License.
# You are free to use, modify, and distribute this code,
# provided that the original copyright notice is retained.
#
# See LICENSE file in the project root for full license information.

# Modified by nnn according to given task

"""
A program that prints reservation information according to task requirements
"""

from datetime import datetime


def convert_reservation_data(reservation: list) -> list:
    """
    Convert data types to meet program requirements

    Parameters:
     reservation (list): Unconverted reservation -> 11 columns

    Returns:
     converted (list): Converted data types
    """

    reservation_id = int(reservation[0])

    name = reservation[1]
    email = reservation[2]
    phone = reservation[3]

    reservation_date = datetime.strptime(reservation[4], "%Y-%m-%d").date()

    time_text = reservation[5].strip()
    time_text = time_text[:8]  # allows "HH:MM" or "HH:MM:SS"

    if len(time_text) == 5:
        reservation_time = datetime.strptime(time_text, "%H:%M").time()
    else:
        reservation_time = datetime.strptime(time_text, "%H:%M:%S").time()

    duration_hours = int(reservation[6])
    price = float(reservation[7])

    confirmed = (reservation[8] == "True")

    reserved_resource = reservation[9]

    created_text = reservation[10].strip()
    created_text = created_text[:19]  # keep "YYYY-MM-DD HH:MM:SS"
    created_at = datetime.strptime(created_text, "%Y-%m-%d %H:%M:%S")

    return [
        reservation_id,
        name,
        email,
        phone,
        reservation_date,
        reservation_time,
        duration_hours,
        price,
        confirmed,
        reserved_resource,
        created_at,
    ]


def fetch_reservations(reservation_file: str) -> list:
    """
    Reads reservations from a file and returns the reservations converted
    You don't need to modify this function!

    Parameters:
     reservation_file (str): Name of the file containing the reservations

    Returns:
     reservations (list): Read and converted reservations
    """
    reservations = []
    with open(reservation_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            fields = line.split("|")
            reservations.append(convert_reservation_data(fields))
    return reservations


def confirmed_reservations(reservations: list[list]) -> None:
    """
    Print confirmed reservations

    Parameters:
     reservations (list): Reservations
    """
    print("1) Confirmed Reservations")
    for r in reservations:
        if r[8]:  # confirmed
            date_str = r[4].strftime("%d.%m.%Y")
            time_str = r[5].strftime("%H.%M")
            print(f"- {r[1]}, {r[9]}, {date_str} at {time_str}")
    print()


def long_reservations(reservations: list[list]) -> None:
    """
    Print long reservations (duration >= 3)

    Parameters:
     reservations (list): Reservations
    """
    print("2) Long Reservations (≥ 3 h)")
    for r in reservations:
        if r[6] >= 3:
            date_str = r[4].strftime("%d.%m.%Y")
            time_str = r[5].strftime("%H.%M")
            print(f"- {r[1]}, {date_str} at {time_str}, duration {r[6]} h, {r[9]}")
    print()


def confirmation_statuses(reservations: list[list]) -> None:
    """
    Print confirmation statuses

    Parameters:
     reservations (list): Reservations
    """
    print("3) Reservation Confirmation Status")
    for r in reservations:
        status = "Confirmed" if r[8] else "NOT Confirmed"
        print(f"{r[1]} → {status}")
    print()


def confirmation_summary(reservations: list[list]) -> None:
    """
    Print confirmation summary

    Parameters:
     reservations (list): Reservations
    """
    print("4) Confirmation Summary")

    confirmed_count = 0
    not_confirmed_count = 0

    for r in reservations:
        if r[8]:
            confirmed_count += 1
        else:
            not_confirmed_count += 1

    print(f"- Confirmed reservations: {confirmed_count} pcs")
    print(f"- Not confirmed reservations: {not_confirmed_count} pcs")
    print()


def total_revenue(reservations: list[list]) -> None:
    """
    Print total revenue from confirmed reservations

    Parameters:
     reservations (list): Reservations
    """
    print("5) Total Revenue from Confirmed Reservations")

    total = 0.0
    for r in reservations:
        if r[8]:
            total += r[6] * r[7]

    total_str = f"{total:.2f}".replace(".", ",")
    print(f"Total revenue from confirmed reservations: {total_str} €")


def main():
    """
    Prints reservation information according to requirements
    Reservation-specific printing is done in functions
    """
    reservations = fetch_reservations("reservations.txt")

    # PART B output only (required)
    confirmed_reservations(reservations)
    long_reservations(reservations)
    confirmation_statuses(reservations)
    confirmation_summary(reservations)
    total_revenue(reservations)


if __name__ == "__main__":
    main()
