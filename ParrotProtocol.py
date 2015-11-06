#!/usr/bin/env python


def generate_request(request_string):
    message = bytearray()
    message.extend(generate_header(request_string))
    message.extend(bytearray(request_string))
    return message


def generate_header(request_string):
    header = bytearray([0])
    header.append(len(request_string) + 3)
    header.append("\x80")
    return header


def get_request(api_string):
    return generate_request("GET " + api_string)


def set_request(api_string, args):
    return generate_request("SET " + api_string + "?arg=" + args)
