#!/usr/bin/python

SPACES = [' ', '\t', '\r', '\n']
OPERATORS = {
'+': '+', 
'-': '-', 
'/': '/', 
'*': '*', 
'=': '==', 
'<=': '<=', 
'>=': '>=', 
'<': '<', 
'>': '>'}
SUBSTIDUDE_WITH_UNDERSCORE = set(['-', '?', '*'])

def lisp_to_tree(lisp_text):
	spaces = []
	code = []
	mode = 'spaces'
	chunk = ''
	parenthesis_level = 0
	
	for char in lisp_text:

		if mode == 'parenthesis':
			chunk += char
			if char == '(':
				parenthesis_level += 1
			if char == ')':
				parenthesis_level -= 1
			if parenthesis_level == 0:
				code += [lisp_to_tree(chunk[1:-1])]
				chunk = ''
				mode = 'spaces'
			continue

		if char in SPACES:
			if mode == 'spaces':
				chunk += char
			else:
				code += [chunk]
				chunk = '' + char
				mode = 'spaces'
		elif char == '(':
			if mode == 'spaces':
				spaces += [chunk]
			else:
				code += [chunk]		
			mode = 'parenthesis'
			parenthesis_level = 1
			chunk = '' + char
		else:
			if mode == 'code':
				if char in SUBSTIDUDE_WITH_UNDERSCORE:
					chunk += '_'
				else:
					chunk += char
			else:
				spaces += [chunk]
				chunk = '' + char
				mode = 'code'
	if mode == 'spaces':
		spaces += [chunk]
	else:
		code += [chunk]
	
	return (spaces, code)

def tree_to_qc(tree):
	if isinstance(tree, str):
		return tree
	(spaces, code) = tree
	qc = ''
	if isinstance(code[0], tuple):
		# list of calls (root)
		for space, chunk in zip(spaces, code):
			qc += space + tree_to_qc(chunk) + ';'
		if len(spaces) > len(code):
			qc += spaces[-1]
	elif code[0] == 'if':
		# if clause
		qc += spaces[0] + 'if('
		qc += spaces[1] + tree_to_qc(code[1]) + '){'
		qc += spaces[2] + tree_to_qc(code[2]) + '}else{'
		qc += spaces[3] + tree_to_qc(code[3]) + '}'
		if len(spaces) > len(code):
			qc += spaces[-1]
	elif code[0] == 'define':
		# define (requires lambda)
		qc += spaces[0] + 'define('
		qc += spaces[1] + tree_to_qc(code[1]) + ', [](){'
		qc += spaces[2] + tree_to_qc(code[2]) + ';})'
		if len(spaces) > len(code):
			qc += spaces[-1]
	elif code[0] in OPERATORS:
		# infix operators
		operator = OPERATORS[code[0]]
		qc += spaces[0] + '(' + spaces[1] + tree_to_qc(code[1]) 
		for space, chunk in zip(spaces[2:], code[2:]):
			qc += operator + space + tree_to_qc(chunk)
		if len(spaces) > len(code):
			qc += ')' + spaces[-1]
		else:
			qc += ')'
	else:
		# default function
		qc += spaces[0] + tree_to_qc(code[0]) + '('
		for space, chunk in zip(spaces[1:-1], code[1:-1]):
			qc += space + tree_to_qc(chunk) + ', ' 
		if len(spaces) > len(code):
			qc += spaces[-2] + tree_to_qc(code[-1]) + ')' + spaces[-1]
		else:
			qc += spaces[-1] + tree_to_qc(code[-1]) + ')'
	return qc

def remove_comments(sourse):
	return '\n'.join([line.split(';')[0] for line in sourse.split('\n')])

from sys import argv
if len(argv) == 2:
	source = open(argv[1]).read()
	clean_sourse = remove_comments(source)
	tree = lisp_to_tree(clean_sourse)
	print 'main(){' + tree_to_qc(tree) + '}'
else:
	print 'give me scheme file name'
