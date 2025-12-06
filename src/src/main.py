import logging
import argparse
import snap7
import ast
import time

import action

FORMAT = "%(asctime)-15s %(levelname)-8s %(message)s"
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.INFO)



def is_valid_address(value):
    ivalue = int(value)
    if ivalue < 0:
        raise argparse.ArgumentTypeError(f"{value} is an invalid address.")
    return ivalue

def is_valid_array(value):
    try:
        return ast.literal_eval(value)
    except (ValueError, SyntaxError):
        raise argparse.ArgumentTypeError(f"{value} is not a valid array.")
    
##### Setup argument for subparsers #####

def add_common_read_args(parser):
    """
    Add common arguments for the read subparser.
    Args:
        parser (argparse.ArgumentParser): The argument parser object.
    """
    
    parser.add_argument("start", type=is_valid_address, help="The starting address to read from")
    parser.add_argument("end", type=is_valid_address, help="The number of items to read")
    parser.add_argument("--count", type=int,required=False, default=1, help="Number of times to read")
    parser.add_argument("--wait", dest="wait", type=float, required=False, default=0.0, help="Wait time between iterations (in seconds)")

def add_common_write_args(parser):
    """
    Add common arguments for the write subparser.
    Args:
        parser (argparse.ArgumentParser): The argument parser object.
    """
    
    parser.add_argument("start", type=is_valid_address, help="The starting address to write to")
    parser.add_argument("data", type=is_valid_array, help="The data to write (as a list or tuple)")
    parser.add_argument("--count", type=int,required=False, default=1, help="Number of times to write")
    parser.add_argument("--wait", dest="wait", type=float, required=False, default=0.0, help="Wait time between iterations (in seconds)")
    

def add_common_fuzz_args(parser):
    """
    Add common arguments for the fuzzing subparser.
    Args:
        parser (argparse.ArgumentParser): The argument parser object.
    """
    parser.add_argument("start", type=is_valid_address, help="The starting address to fuzz")
    parser.add_argument("end", type=is_valid_address, help="The ending address to fuzz")
    parser.add_argument("--count", type=int,required=False,default=1, help="Number of fuzzing iterations")
    parser.add_argument("--wait", dest="wait", type=float, required=False, default=0.0, help="Wait time between iterations (in seconds)")
    parser.add_argument("--range", type=int, required=False, default=10, help="The range of values to fuzz 0-255 (default: 10)")
    parser.add_argument("--safe", action="store_true", help="Enable safe mode for fuzzing (default: False)")

def create_arg_parser():
    """Create the argument parser for the S7 Client Action Library.
    Returns:
        argparse.ArgumentParser: The argument parser object.
    """
    parser = argparse.ArgumentParser(description="S7 Client Action Library")

    parser.add_argument(
        "-a",
        dest="ip",
        required=True,
        help="The target device IP address"
    )
    parser.add_argument(
        "-p", "--port",
        type=int,
        dest="port",
        default=102,
        help="The target device S7 port (default: 102)"
    )
    parser.add_argument(
        "-r", "--rack", 
        type=int, 
        default=0, 
        help="The rack number"
    )
    parser.add_argument(
        "-s", "--slot",
        type=int, 
        default=0, 
        help="The slot number"
    )

    parser.add_argument(
        "--area",
        choices=["DB","PA","PE", "MB", "CT", "TM"],
        required=False,
        default="DB",
        help="The area to read/write from/to")
    
    
    parser.add_argument(
        "--db_number", 
        dest="db_number",
        type=int,
        default=0, 
        help="number of the DB to write to")

    subparsers = parser.add_subparsers(help="Action to be taken", required=True, dest="action")

    read_parser = subparsers.add_parser("read", help="Read data from the PLC")
    add_common_read_args(read_parser)
    
    write_parser = subparsers.add_parser("write", help="Write data to the PLC")
    add_common_write_args(write_parser)

    fuzz_parser = subparsers.add_parser("fuzz", help="Fuzz the PLC")
    add_common_fuzz_args(fuzz_parser)

    subparsers.add_parser("gather_info", help="Gather information from the PLC")
    
    return parser

def print_register(register, NUMBER, ADDRESS):
    output = []
    offset = int(ADDRESS) % 8
    result = [bits[::-1] for bits in ['0' * (8 - len(bin(x)[2:])) + bin(x)[2:] for x in register]]
    for k in range(NUMBER * 8):
        output.append(result[0][k])  
        if 8 < offset + int(NUMBER):
            size_result = len(result)
            for l in range(1, size_result):
                for m in range(0, 8):
                    output.append(result[l][m])
    print('===Outputs===')
    for j in range(0, int(NUMBER)):
        print("Output " + str(int(ADDRESS) + j) + " : " + output[j])
    return None 


def do_action(client, args):
    """Perform the action specified by the user.

    Possible actions:
    - read: Read data from the PLC
    - write: Write data to the PLC
    - fuzz: Fuzz the PLC
    - gather_info: Gather information from the PLC
    
    Args:
        client: The snap7 client object.
        args: The parsed arguments from argparse.
    """
    try:
        if args.action.lower() == "read":
            log.info("[*] Read data")
            for i in range(args.count):
                result = action.read_area(client, args.area, args.db_number, args.start, args.end)
                log.info(f"Register output: {result}")
                for j in range(args.start, args.end):
                    log.info(f"Register {j}: {result[j]}")
                time.sleep(args.wait)
            log.info("Read successful.")
        elif args.action.lower() == "write":
            log.info("[*] Write data")
            for i in range(args.count):
                action.write_area(client, args.area, args.db_number, args.start, args.data)
                log.info(f"Data to write: {args.data}")
                for j in range(len(args.data)):
                    log.info(f"Register {args.start + j}: {args.data[j]}")
                
                time.sleep(args.wait)
            log.info("Write successful.")
        elif args.action.lower() == "fuzz":
            log.info("[*] Fuzz data")
            for i in range(args.count):
                action.fuzz_area(client, args.area, args.db_number, args.start, args.end, safe=args.safe, limit=args.range)
                time.sleep(args.wait)
            log.info("Fuzzing successful.")
        elif args.action.lower() == "gather_info":
            log.info("[*] Gather information")
            action.gather_info(client)
            log.info("Gathering information successful.")
   
        else:
            log.error(f"Unknown action: {args.action}")
                    
    except AttributeError as e:
        log.error(f"{args}")
        log.error(f"Snap7 error: No such area: {e}")

def run():
    args = create_arg_parser().parse_args()
    client = snap7.client.Client()
    client.connect(args.ip, rack=args.rack, slot=args.slot, tcp_port=args.port)
    connection = client.get_connected()
    if not connection:
        log.error("Connection failed.")
        return
    else:
        log.info("Connected to PLC.")
    do_action(client, args)
    client.disconnect()

if __name__ == "__main__":
    run()
