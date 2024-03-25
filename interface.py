#!../venv/bin/python
import asyncio
import chess
import os
import subprocess
import sys

from re import split as rsplit
from typing import Dict, List, Tuple


def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


engine_script = get_resource_path('engine.py')


def debug_print(*message, **kwargs):
    """Used for debugging purposes when debug mode is on"""
    global debug
    print(*message, **kwargs)
    if debug:
        with open("debug.txt", "a") as f:
            f.write(f"Engine: {message}\n")
            

async def read_input(input_queue, output_queue):
    while True:
        gui_input = await asyncio.get_event_loop().run_in_executor(None, input)
        await input_queue.put(gui_input)
        if gui_input == "quit" or gui_input == "quit\n":
            break


async def print_from_queue(output_queue):
    while True:
        while not output_queue.empty():
            debug_print(await output_queue.get())
        await asyncio.sleep(0.1)


async def uci(output_queue):
    await output_queue.put("id name PuffinChess")
    await output_queue.put("id authors Michael Ruman and Peter Popluhar")
    await output_queue.put("uciok")


async def set_debug(token: str, output_queue):
    global debug
    match token:
        case "on":
            debug = True
            await output_queue.put("Started new debug session")
        case "off":
            debug = False
        case _:
            await output_queue.put(f"Undefined option for debug: {token}")


async def setoption(tokens: list[str], output_queue):
    await output_queue.put(f"Unknown option {tokens[0]}")


def ucinewgame():
    return chess.STARTING_FEN


def position(tokens: list[str]):
    if tokens[0] == "fen":
        internal_fen = " ".join(tokens[1:7])
    else:
        internal_fen = chess.STARTING_FEN
    board = chess.Board(internal_fen)
    
    if len(tokens) > 1 and tokens[1] == "moves":
        for i in range(2, len(tokens)):
            board.push(chess.Move.from_uci(tokens[i]))
    if len(tokens) > 7 and tokens[7] == "moves":
        for i in range(8, len(tokens)):
            board.push(chess.Move.from_uci(tokens[i]))
    internal_fen = board.fen()
    
    return internal_fen


async def go(tokens: list[str], 
             fen: str,
            ) -> asyncio.subprocess.Process:
    # we won't support ponder and mate
    # and we won't even count nodes
    global debug

    debug_arg = "on" if debug else "off"
    color = str.split(fen)[1]
    searchmoves = []
    if "searchmoves" in tokens:
        legal_moves = [str(x) for x in chess.Board(fen).legal_moves]
        
        for move in tokens[tokens.index("searchmoves") + 1:]:
            if move not in legal_moves:
                break
            searchmoves.append(move)
            
    if "depth" in tokens:
        depth = tokens[tokens.index("depth") + 1]
        engine = await asyncio.create_subprocess_exec(
            "python", "-u", engine_script, fen, "d", depth, debug_arg, *searchmoves, 
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        return engine
        
    elif "infinite" in tokens:
        movetime = "86400000"

    elif "movetime" in tokens:
        movetime = tokens[tokens.index("movetime") + 1]
    
    elif color+"time" in tokens:
        movetime = int(tokens[tokens.index(color+"time") + 1])/40
        if color+"inc" in tokens:
            movetime += int(tokens[tokens.index(color+"inc") + 1])
        movetime = str(movetime)

    else:
        movetime = "86400000"
        
    engine = await asyncio.create_subprocess_exec(
        "python", "-u", engine_script, fen, "t", movetime, debug_arg, *searchmoves,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    return engine


async def engine_handler(engine, output_queue):
    while True:
        if engine.stdout.at_eof():
            break
        line = await engine.stdout.readline()
        if line:
            await output_queue.put(line.decode().rstrip())
        else:
            await asyncio.sleep(0.1)

async def engine_error_handler(engine, output_queue):
    while True:
        if engine.stderr.at_eof():
            break
        line = await engine.stderr.readline()
        if line:
            await output_queue.put(f"Error: {line.decode().rstrip()}")


async def stop(engine, output_queue):
    try:
        engine.terminate()
        await engine.wait()
    except ProcessLookupError:
        pass
    except Exception as e:
        await output_queue.put(f"Error stopping engine: {e}")
        

def ponderhit():
    # Won't implement this
    pass


async def main():
    """
    Accepts commands from the GUI, parses them as UCI commands
    and calls corresponding functions
    """
    global debug

    input_queue = asyncio.Queue()
    output_queue = asyncio.Queue()

    fen = None
    engine = None

    reader = asyncio.create_task(read_input(input_queue, output_queue))
    printer = asyncio.create_task(print_from_queue(output_queue))

    while True:
        if not input_queue.empty():
            command = await input_queue.get()
            if debug:
                with open("debug.txt", "a") as f:
                    f.write(f"UCI: {command}\n")

            # we split the command with any number of whitespaces as the separator (using regex)
            tokens = rsplit(pattern=r"[\s\t]+", string=command.strip())
            if engine and engine.stdout.at_eof():
                await stop(engine, output_queue)
                engine = None
            if engine:
                    
                if tokens[0] == "stop":
                    await stop(engine, output_queue)
                    engine = None
                else:
                    debug_print("Engine is running. Please, use 'stop' to terminate it.")
            else:     
                match tokens[0]:
                    case "uci":
                        await uci(output_queue)

                    case "debug":
                        if len(tokens) > 1:
                            await set_debug(tokens[1], output_queue)

                    case "isready":
                        await output_queue.put("readyok")

                    case "setoption":
                        await setoption(tokens[1:], output_queue)

                    case "ucinewgame":
                        fen = ucinewgame()

                    case "position":
                        fen = position(tokens[1:])

                    case "go":
                        if fen is not None:
                            engine = await go(tokens[1:], fen)
                            await asyncio.create_task(engine_handler(engine, output_queue))
                            await asyncio.create_task(engine_error_handler(engine, output_queue))
                        else:
                            await output_queue.put("No position specified")
                            
                    case "ponderhit":
                        ponderhit()

                    case "quit":
                        if engine is not None:
                            await stop(engine, output_queue)
                        reader.cancel()
                        printer.cancel()
                        asyncio.get_running_loop().stop()
                        sys.exit()

                    case "parameters":
                        debug_print(f"debug {debug}, fen {fen}, engine {engine}")

                    case _:
                        debug_print(f"Unknown command {command}")

        await asyncio.sleep(0.1)
            

if __name__ == "__main__":
    debug = False
    asyncio.run(main())
