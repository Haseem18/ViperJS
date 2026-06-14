import sys, math, random, re, datetime, time

# ═══════════════════════════════════════════
#  TOKENS
# ═══════════════════════════════════════════
TT_NUMBER='NUMBER';TT_STRING='STRING';TT_BOOL='BOOL';TT_NULL='NULL'
TT_UNDEF='UNDEFINED';TT_IDENT='IDENT';TT_KEYWORD='KEYWORD';TT_OP='OP'
TT_LPAREN='LPAREN';TT_RPAREN='RPAREN';TT_LBRACE='LBRACE';TT_RBRACE='RBRACE'
TT_LBRACKET='LBRACKET';TT_RBRACKET='RBRACKET';TT_SEMI='SEMI';TT_COMMA='COMMA'
TT_DOT='DOT';TT_COLON='COLON';TT_QUESTION='QUESTION';TT_SPREAD='SPREAD'
TT_ARROW='ARROW';TT_EOF='EOF';TT_TEMPLATE='TEMPLATE'

KEYWORDS={
    'let','const','var','if','else','while','for','do','function',
    'return','true','false','null','undefined','new','typeof',
    'switch','case','break','default','continue','of','in',
    'class','this','delete','void','instanceof','throw','try','catch','finally',
    'async','await'
}

class Token:
    def __init__(self,t,v): self.type=t; self.value=v
    def __repr__(self): return f'Token({self.type},{self.value!r})'

# ═══════════════════════════════════════════
#  JS ERROR CLASSES (Task 1)
# ═══════════════════════════════════════════
class JSError:
    def __init__(self,name,msg): self.name=name; self.message=msg
    def __str__(self): return f'{self.name}: {self.message}'
    def __repr__(self): return str(self)

class JSReferenceError(JSError):
    def __init__(self,msg): super().__init__('ReferenceError',msg)
class JSTypeError(JSError):
    def __init__(self,msg): super().__init__('TypeError',msg)
class JSSyntaxError(JSError):
    def __init__(self,msg): super().__init__('SyntaxError',msg)
class JSRangeError(JSError):
    def __init__(self,msg): super().__init__('RangeError',msg)

# ═══════════════════════════════════════════
#  LEXER
# ═══════════════════════════════════════════
class Lexer:
    def __init__(self,src): self.src=src; self.pos=0; self.tokens=[]
    def cur(self): return self.src[self.pos] if self.pos<len(self.src) else None
    def peek(self,o=1):
        p=self.pos+o; return self.src[p] if p<len(self.src) else None
    def adv(self):
        c=self.src[self.pos]; self.pos+=1; return c

    def tokenize(self):
        while self.pos<len(self.src):
            c=self.cur()
            if c in ' \t\r\n': self.adv(); continue
            if c=='/' and self.peek()=='/':
                while self.pos<len(self.src) and self.cur()!='\n': self.adv()
                continue
            if c=='/' and self.peek()=='*':
                self.adv(); self.adv()
                while self.pos<len(self.src):
                    if self.cur()=='*' and self.peek()=='/': self.adv(); self.adv(); break
                    self.adv()
                continue
            if c=='`': self.tokens.append(self._tmpl()); continue
            if c in ('"',"'"): self.tokens.append(self._str(c)); continue
            if c.isdigit() or (c=='.' and self.peek() and self.peek().isdigit()):
                self.tokens.append(self._num()); continue
            if c.isalpha() or c in '_$': self.tokens.append(self._ident()); continue
            if c=='.' and self.peek()=='.' and self.peek(2)=='.':
                self.adv();self.adv();self.adv(); self.tokens.append(Token(TT_SPREAD,'...')); continue
            if c=='=':
                if self.peek()=='>': self.adv();self.adv(); self.tokens.append(Token(TT_ARROW,'=>'))
                elif self.peek()=='=':
                    self.adv();self.adv()
                    if self.cur()=='=': self.adv(); self.tokens.append(Token(TT_OP,'==='))
                    else: self.tokens.append(Token(TT_OP,'=='))
                else: self.adv(); self.tokens.append(Token(TT_OP,'='))
                continue
            if c=='!':
                if self.peek()=='=':
                    self.adv();self.adv()
                    if self.cur()=='=': self.adv(); self.tokens.append(Token(TT_OP,'!=='))
                    else: self.tokens.append(Token(TT_OP,'!='))
                else: self.adv(); self.tokens.append(Token(TT_OP,'!'))
                continue
            if c=='<':
                if self.peek()=='=': self.adv();self.adv(); self.tokens.append(Token(TT_OP,'<='))
                else: self.adv(); self.tokens.append(Token(TT_OP,'<'))
                continue
            if c=='>':
                if self.peek()=='=': self.adv();self.adv(); self.tokens.append(Token(TT_OP,'>='))
                else: self.adv(); self.tokens.append(Token(TT_OP,'>'))
                continue
            if c=='&' and self.peek()=='&': self.adv();self.adv(); self.tokens.append(Token(TT_OP,'&&')); continue
            if c=='|' and self.peek()=='|': self.adv();self.adv(); self.tokens.append(Token(TT_OP,'||')); continue
            if c=='?' and self.peek()=='?': self.adv();self.adv(); self.tokens.append(Token(TT_OP,'??')); continue
            if c=='*' and self.peek()=='*':
                self.adv();self.adv()
                if self.cur()=='=': self.adv(); self.tokens.append(Token(TT_OP,'**='))
                else: self.tokens.append(Token(TT_OP,'**'))
                continue
            cmp={'+':'+=','-':'-=','*':'*=','/':'/=','%':'%='}
            if c in cmp:
                if self.peek()==c and c in ('+','-'): self.adv();self.adv(); self.tokens.append(Token(TT_OP,c+c))
                elif self.peek()=='=': self.adv();self.adv(); self.tokens.append(Token(TT_OP,cmp[c]))
                else: self.adv(); self.tokens.append(Token(TT_OP,c))
                continue
            sm={'(':TT_LPAREN,')':TT_RPAREN,'{':TT_LBRACE,'}':TT_RBRACE,
                '[':TT_LBRACKET,']':TT_RBRACKET,';':TT_SEMI,',':TT_COMMA,
                '.':TT_DOT,':':TT_COLON,'?':TT_QUESTION}
            if c in sm: self.adv(); self.tokens.append(Token(sm[c],c)); continue
            self.adv()
        self.tokens.append(Token(TT_EOF,None))
        return self.tokens

    def _str(self,q):
        self.adv(); s=''
        while self.pos<len(self.src) and self.cur()!=q:
            if self.cur()=='\\':
                self.adv()
                esc={'n':'\n','t':'\t','r':'\r','\\':'\\','"':'"',"'":"'",'`':'`'}
                s+=esc.get(self.cur(),self.cur())
            else: s+=self.cur()
            self.adv()
        self.adv(); return Token(TT_STRING,s)

    def _tmpl(self):
        self.adv(); s=''
        while self.pos<len(self.src) and self.cur()!='`':
            if self.cur()=='\\':
                self.adv()
                esc={'n':'\n','t':'\t','r':'\r','\\':'\\','`':'`'}
                s+=esc.get(self.cur(),self.cur())
            else: s+=self.cur()
            self.adv()
        self.adv(); return Token(TT_TEMPLATE,s)

    def _num(self):
        s=''
        while self.pos<len(self.src) and (self.cur().isdigit() or self.cur()=='.'):
            s+=self.adv()
        return Token(TT_NUMBER, float(s) if '.' in s else int(s))

    def _ident(self):
        s=''
        while self.pos<len(self.src) and (self.cur().isalnum() or self.cur() in '_$'):
            s+=self.adv()
        if s in ('true','false'): return Token(TT_BOOL, s=='true')
        if s=='null': return Token(TT_NULL,None)
        if s=='undefined': return Token(TT_UNDEF,'undefined')
        if s in KEYWORDS: return Token(TT_KEYWORD,s)
        return Token(TT_IDENT,s)

# ═══════════════════════════════════════════
#  AST NODES
# ═══════════════════════════════════════════
class Node: pass
class Program(Node):
    def __init__(self,b): self.body=b
class VarDecl(Node):
    def __init__(self,k,d): self.kind=k; self.declarations=d
class Declarator(Node):
    def __init__(self,n,i,dest=False,keys=None,arr_dest=False):
        self.name=n; self.init=i; self.is_destructure=dest
        self.keys=keys; self.is_array_dest=arr_dest
class ExprStmt(Node):
    def __init__(self,e): self.expr=e
class AssignExpr(Node):
    def __init__(self,op,l,r): self.op=op; self.left=l; self.right=r
class BinOp(Node):
    def __init__(self,op,l,r): self.op=op; self.left=l; self.right=r
class UnaryOp(Node):
    def __init__(self,op,o,pre=True): self.op=op; self.operand=o; self.prefix=pre
class Literal(Node):
    def __init__(self,v): self.value=v
class Identifier(Node):
    def __init__(self,n): self.name=n
class IfStmt(Node):
    def __init__(self,t,c,a): self.test=t; self.consequent=c; self.alternate=a
class WhileStmt(Node):
    def __init__(self,t,b): self.test=t; self.body=b
class DoWhileStmt(Node):
    def __init__(self,t,b): self.test=t; self.body=b
class ForStmt(Node):
    def __init__(self,i,t,u,b): self.init=i; self.test=t; self.update=u; self.body=b
class ForOfStmt(Node):
    def __init__(self,k,v,it,b): self.kind=k; self.var=v; self.iterable=it; self.body=b
class ForInStmt(Node):
    def __init__(self,k,v,o,b): self.kind=k; self.var=v; self.obj=o; self.body=b
class BlockStmt(Node):
    def __init__(self,b): self.body=b
class FuncDecl(Node):
    def __init__(self,n,p,b): self.name=n; self.params=p; self.body=b
class FuncExpr(Node):
    def __init__(self,n,p,b): self.name=n; self.params=p; self.body=b
class ArrowFunc(Node):
    def __init__(self,p,b,expr=False): self.params=p; self.body=b; self.expression=expr
class AsyncFuncDecl(Node):
    def __init__(self,n,p,b): self.name=n; self.params=p; self.body=b
class AsyncFuncExpr(Node):
    def __init__(self,n,p,b): self.name=n; self.params=p; self.body=b
class AsyncArrowFunc(Node):
    def __init__(self,p,b): self.params=p; self.body=b
class AwaitExpr(Node):
    def __init__(self,a): self.argument=a
class ReturnStmt(Node):
    def __init__(self,v): self.value=v
class CallExpr(Node):
    def __init__(self,c,a): self.callee=c; self.args=a
class MemberExpr(Node):
    def __init__(self,o,p,computed=False): self.obj=o; self.prop=p; self.computed=computed
class ArrayExpr(Node):
    def __init__(self,e): self.elements=e
class ObjectExpr(Node):
    def __init__(self,p): self.properties=p
class Property(Node):
    def __init__(self,k,v): self.key=k; self.value=v
class SpreadElement(Node):
    def __init__(self,a): self.argument=a
class TemplateLiteral(Node):
    def __init__(self,r,e): self.raw=r; self.expressions=e
class TernaryExpr(Node):
    def __init__(self,t,c,a): self.test=t; self.consequent=c; self.alternate=a
class NewExpr(Node):
    def __init__(self,c,a): self.callee=c; self.args=a
class TypeofExpr(Node):
    def __init__(self,o): self.operand=o
class SwitchStmt(Node):
    def __init__(self,d,c): self.discriminant=d; self.cases=c
class SwitchCase(Node):
    def __init__(self,t,c): self.test=t; self.consequent=c
class BreakStmt(Node): pass
class ContinueStmt(Node): pass
class ThrowStmt(Node):
    def __init__(self,a): self.argument=a
class TryCatch(Node):
    def __init__(self,b,h,f): self.block=b; self.handler=h; self.finalizer=f
class Param(Node):
    def __init__(self,n,rest=False,default=None): self.name=n; self.rest=rest; self.default=default

# ═══════════════════════════════════════════
#  CONTROL FLOW SIGNALS
# ═══════════════════════════════════════════
class ReturnSignal(Exception):
    def __init__(self,v): self.value=v
class BreakSignal(Exception): pass
class ContinueSignal(Exception): pass
class ThrowSignal(Exception):
    def __init__(self,v): self.value=v

class AwaitSuspend(Exception):
    """Raised when await must suspend an async function."""
    def __init__(self,promise,resume_fn=None):
        self.promise=promise; self.resume_fn=resume_fn

# ═══════════════════════════════════════════
#  PROMISE ENGINE
# ═══════════════════════════════════════════
class JSPromise:
    PENDING='pending'; FULFILLED='fulfilled'; REJECTED='rejected'
    def __init__(self,interp):
        self.state=self.PENDING; self.value='undefined'; self.reason='undefined'
        self._then_cbs=[]; self._catch_cbs=[]; self._finally_cbs=[]
        self._interp=interp

    def resolve(self,value):
        if self.state!=self.PENDING: return
        if isinstance(value,JSPromise):
            value._add_then(self.resolve,self.reject); return
        self.state=self.FULFILLED; self.value=value
        for cb,np in self._then_cbs: self._invoke(cb,value,np)
        for cb,np in self._finally_cbs: self._invoke(cb,None,None); np.resolve(value) if np else None

    def reject(self,reason):
        if self.state!=self.PENDING: return
        self.state=self.REJECTED; self.reason=reason
        for cb,np in self._catch_cbs: self._invoke(cb,reason,np)
        for cb,np in self._finally_cbs: self._invoke(cb,None,None); np.reject(reason) if np else None

    def _invoke(self,cb,arg,next_p):
        if cb is None:
            if next_p: next_p.resolve(arg)
            return
        interp=self._interp
        def _task():
            try:
                if isinstance(cb,JSFunction): result=interp._call_fn(cb,[arg] if arg is not None else [])
                elif callable(cb): result=cb(arg) if arg is not None else cb()
                else: result='undefined'
                if next_p: next_p.resolve(result)
            except ReturnSignal as r:
                if next_p: next_p.resolve(r.value)
            except ThrowSignal as e:
                if next_p: next_p.reject(e.value)
            except Exception as e:
                if next_p: next_p.reject(str(e))
        interp._microtask_queue.append((_task,[]))

    def _add_then(self,on_f,on_r=None):
        if self.state==self.FULFILLED: self._invoke(on_f,self.value,None)
        elif self.state==self.REJECTED:
            if on_r: self._invoke(on_r,self.reason,None)
        else:
            self._then_cbs.append((on_f,None))
            if on_r: self._catch_cbs.append((on_r,None))

    def then(self,*args):
        on_f=args[0] if len(args)>0 else None
        on_r=args[1] if len(args)>1 else None
        np=JSPromise(self._interp)
        if self.state==self.FULFILLED: self._invoke(on_f,self.value,np)
        elif self.state==self.REJECTED:
            if on_r: self._invoke(on_r,self.reason,np)
            else: np.reject(self.reason)
        else:
            self._then_cbs.append((on_f,np))
            self._catch_cbs.append((on_r,np) if on_r else (None,np))
        return np

    def catch(self,*args):
        on_r=args[0] if args else None
        np=JSPromise(self._interp)
        if self.state==self.REJECTED: self._invoke(on_r,self.reason,np)
        elif self.state==self.FULFILLED: np.resolve(self.value)
        else:
            self._catch_cbs.append((on_r,np))
            self._then_cbs.append((None,np))
        return np

    def finally_(self,*args):
        cb=args[0] if args else None
        np=JSPromise(self._interp)
        if self.state!=self.PENDING:
            if cb:
                try:
                    if isinstance(cb,JSFunction): self._interp._call_fn(cb,[])
                    elif callable(cb): cb()
                except: pass
            if self.state==self.FULFILLED: np.resolve(self.value)
            else: np.reject(self.reason)
        else: self._finally_cbs.append((cb,np))
        return np

# ═══════════════════════════════════════════
#  JS MAP (Task 2)
# ═══════════════════════════════════════════
class JSMap:
    def __init__(self,interp,init=None):
        self._keys=[]; self._vals=[]; self._interp=interp
        if init and isinstance(init,list):
            for pair in init:
                if isinstance(pair,list) and len(pair)>=2:
                    self._set(pair[0],pair[1])

    def _find(self,key):
        for i,k in enumerate(self._keys):
            if k==key or (isinstance(k,(int,float)) and isinstance(key,(int,float)) and k==key):
                return i
        return -1

    def _set(self,key,val):
        i=self._find(key)
        if i>=0: self._vals[i]=val
        else: self._keys.append(key); self._vals.append(val)
        return self

    def _get(self,key):
        i=self._find(key)
        return self._vals[i] if i>=0 else 'undefined'

    def _has(self,key): return self._find(key)>=0

    def _delete(self,key):
        i=self._find(key)
        if i>=0: self._keys.pop(i); self._vals.pop(i); return True
        return False

    def _clear(self): self._keys=[]; self._vals=[]

    def _keys_iter(self): return list(self._keys)
    def _vals_iter(self): return list(self._vals)
    def _entries_iter(self): return [[k,v] for k,v in zip(self._keys,self._vals)]

    def _forEach(self,fn):
        for k,v in zip(self._keys,self._vals):
            self._interp._call_cb(fn,[v,k,self])
        return 'undefined'

    def __iter__(self): return iter(self._entries_iter())
    def __len__(self): return len(self._keys)

# ═══════════════════════════════════════════
#  JS SET (Task 3)
# ═══════════════════════════════════════════
class JSSet:
    def __init__(self,interp,init=None):
        self._items=[]; self._interp=interp
        if init and isinstance(init,list):
            for item in init: self._add(item)

    def _find(self,val):
        for i,v in enumerate(self._items):
            if v==val or (isinstance(v,(int,float)) and isinstance(val,(int,float)) and v==val):
                return i
        return -1

    def _add(self,val):
        if self._find(val)<0: self._items.append(val)
        return self

    def _has(self,val): return self._find(val)>=0

    def _delete(self,val):
        i=self._find(val)
        if i>=0: self._items.pop(i); return True
        return False

    def _clear(self): self._items=[]

    def _values(self): return list(self._items)
    def _keys(self): return list(self._items)
    def _entries(self): return [[v,v] for v in self._items]

    def _forEach(self,fn):
        for v in self._items: self._interp._call_cb(fn,[v,v,self])
        return 'undefined'

    def __iter__(self): return iter(self._items)
    def __len__(self): return len(self._items)

# ═══════════════════════════════════════════
#  JS FUNCTION WRAPPER
# ═══════════════════════════════════════════
class JSFunction:
    def __init__(self,name,params,body,closure,is_async=False):
        self.name=name; self.params=params; self.body=body
        self.closure=closure; self.is_async=is_async

# ═══════════════════════════════════════════
#  ENVIRONMENT  (Task 1 — const + duplicate tracking)
# ═══════════════════════════════════════════
class Environment:
    def __init__(self,parent=None):
        self.vars={}; self.consts=set(); self.parent=parent

    def get(self,n):
        if n in self.vars: return self.vars[n]
        if self.parent: return self.parent.get(n)
        raise ThrowSignal(JSReferenceError(f'{n} is not defined'))

    def set(self,n,v):
        if n in self.vars:
            if n in self.consts:
                raise ThrowSignal(JSTypeError('Assignment to constant variable.'))
            self.vars[n]=v; return
        if self.parent and self.parent.has(n): self.parent.set(n,v); return
        self.vars[n]=v

    def define(self,n,v,const=False):
        self.vars[n]=v
        if const: self.consts.add(n)

    def define_let(self,n,v,kind='let'):
        # duplicate check only in same scope
        if n in self.vars:
            raise ThrowSignal(JSSyntaxError(f"Identifier '{n}' has already been declared"))
        self.vars[n]=v
        if kind=='const': self.consts.add(n)

    def has(self,n):
        if n in self.vars: return True
        if self.parent: return self.parent.has(n)
        return False

    def has_local(self,n): return n in self.vars

# ═══════════════════════════════════════════
#  PARSER
# ═══════════════════════════════════════════
class Parser:
    def __init__(self,tokens): self.tokens=tokens; self.pos=0
    def cur(self): return self.tokens[self.pos]
    def _tv(self,t):
        if t.value is True: return 'true'
        if t.value is False: return 'false'
        if t.value is None: return 'null'
        return str(t.value)
    def peek(self,o=1):
        p=self.pos+o; return self.tokens[p] if p<len(self.tokens) else self.tokens[-1]
    def adv(self):
        t=self.tokens[self.pos]
        if self.pos<len(self.tokens)-1: self.pos+=1
        return t
    def expect(self,tp,v=None):
        t=self.cur()
        if t.type!=tp: raise ThrowSignal(JSSyntaxError(f"Unexpected token '{self._tv(t)}'"))
        if v is not None and t.value!=v: raise ThrowSignal(JSSyntaxError(f"Unexpected token '{self._tv(t)}'"))
        return self.adv()
    def match(self,tp,v=None):
        t=self.cur()
        if t.type==tp and (v is None or t.value==v): return self.adv()
        return None
    def skips(self):
        while self.cur().type==TT_SEMI: self.adv()

    def parse(self):
        body=[]
        while self.cur().type!=TT_EOF:
            s=self.parse_stmt()
            if s: body.append(s)
        return Program(body)

    def parse_stmt(self):
        self.skips()
        if self.cur().type==TT_EOF: return None
        t=self.cur()
        if t.type==TT_KEYWORD:
            v=t.value
            if v in ('let','const','var'): return self.parse_var()
            if v=='if': return self.parse_if()
            if v=='while': return self.parse_while()
            if v=='do': return self.parse_do()
            if v=='for': return self.parse_for()
            if v=='function': return self.parse_fdecl()
            if v=='return': return self.parse_return()
            if v=='switch': return self.parse_switch()
            if v=='break': self.adv(); self.skips(); return BreakStmt()
            if v=='continue': self.adv(); self.skips(); return ContinueStmt()
            if v=='throw': return self.parse_throw()
            if v=='try': return self.parse_try()
            if v=='async': return self.parse_async_stmt()
        if t.type==TT_LBRACE: return self.parse_block()
        e=self.parse_expr()
        self.skips()
        return ExprStmt(e)

    def parse_block(self):
        self.expect(TT_LBRACE)
        body=[]
        while self.cur().type!=TT_RBRACE and self.cur().type!=TT_EOF:
            s=self.parse_stmt()
            if s: body.append(s)
        self.expect(TT_RBRACE)
        return BlockStmt(body)

    def parse_var(self):
        kind=self.adv().value
        decls=[]
        while True:
            if self.cur().type==TT_LBRACE: decls.append(self.parse_dest(kind))
            elif self.cur().type==TT_LBRACKET: decls.append(self.parse_arr_dest(kind))
            else:
                n=self.expect(TT_IDENT).value
                i=None
                if self.match(TT_OP,'='): i=self.parse_assign_expr()
                elif kind=='const':
                    raise ThrowSignal(JSSyntaxError('Missing initializer in const declaration'))
                decls.append(Declarator(n,i))
            if not self.match(TT_COMMA): break
        self.skips()
        return VarDecl(kind,decls)

    def parse_dest(self,kind):
        self.expect(TT_LBRACE); keys=[]
        while self.cur().type!=TT_RBRACE:
            k=self.expect(TT_IDENT).value; a=k
            if self.match(TT_COLON): a=self.expect(TT_IDENT).value
            keys.append((k,a)); self.match(TT_COMMA)
        self.expect(TT_RBRACE); self.expect(TT_OP,'=')
        i=self.parse_assign_expr()
        return Declarator(None,i,dest=True,keys=keys)

    def parse_arr_dest(self,kind):
        self.expect(TT_LBRACKET); keys=[]
        while self.cur().type!=TT_RBRACKET:
            if self.cur().type==TT_COMMA: keys.append(None); self.adv()
            else: keys.append(self.expect(TT_IDENT).value); self.match(TT_COMMA)
        self.expect(TT_RBRACKET); self.expect(TT_OP,'=')
        i=self.parse_assign_expr()
        return Declarator(None,i,dest=True,keys=keys,arr_dest=True)

    def parse_if(self):
        self.adv(); self.expect(TT_LPAREN)
        t=self.parse_expr(); self.expect(TT_RPAREN)
        c=self.parse_stmt(); a=None
        if self.cur().type==TT_KEYWORD and self.cur().value=='else':
            self.adv(); a=self.parse_stmt()
        return IfStmt(t,c,a)

    def parse_while(self):
        self.adv(); self.expect(TT_LPAREN)
        t=self.parse_expr(); self.expect(TT_RPAREN)
        b=self.parse_stmt(); return WhileStmt(t,b)

    def parse_do(self):
        self.adv(); b=self.parse_stmt()
        self.expect(TT_KEYWORD,'while'); self.expect(TT_LPAREN)
        t=self.parse_expr(); self.expect(TT_RPAREN); self.skips()
        return DoWhileStmt(t,b)

    def parse_for(self):
        self.adv(); self.expect(TT_LPAREN)
        if self.cur().type==TT_KEYWORD and self.cur().value in ('let','const','var'):
            kind=self.adv().value; vn=self.expect(TT_IDENT).value
            if self.cur().type==TT_KEYWORD and self.cur().value=='of':
                self.adv(); it=self.parse_assign_expr(); self.expect(TT_RPAREN)
                return ForOfStmt(kind,vn,it,self.parse_stmt())
            if self.cur().type==TT_KEYWORD and self.cur().value=='in':
                self.adv(); obj=self.parse_assign_expr(); self.expect(TT_RPAREN)
                return ForInStmt(kind,vn,obj,self.parse_stmt())
            ie=None
            if self.match(TT_OP,'='): ie=self.parse_assign_expr()
            init=VarDecl(kind,[Declarator(vn,ie)])
        elif self.cur().type==TT_SEMI: init=None
        else: init=ExprStmt(self.parse_expr())
        self.expect(TT_SEMI)
        test=None if self.cur().type==TT_SEMI else self.parse_expr()
        self.expect(TT_SEMI)
        upd=None if self.cur().type==TT_RPAREN else self.parse_expr()
        self.expect(TT_RPAREN)
        return ForStmt(init,test,upd,self.parse_stmt())

    def parse_fdecl(self):
        self.adv(); n=self.expect(TT_IDENT).value
        p=self.parse_params(); b=self.parse_block()
        return FuncDecl(n,p,b)

    def parse_async_stmt(self):
        self.adv()
        if self.cur().type==TT_KEYWORD and self.cur().value=='function':
            self.adv(); n=self.expect(TT_IDENT).value
            p=self.parse_params(); b=self.parse_block()
            node=AsyncFuncExpr(n,p,b)
            return ExprStmt(AssignExpr('=',Identifier(n),node))
        node=self.parse_async_arrow()
        self.skips()
        return ExprStmt(node)

    def parse_async_arrow(self):
        if self.cur().type==TT_LPAREN:
            p=self.parse_params(); self.expect(TT_ARROW)
            b=self.parse_arrow_body(); return AsyncArrowFunc(p,b)
        if self.cur().type==TT_IDENT:
            n=self.adv().value
            if self.cur().type==TT_ARROW:
                self.adv(); b=self.parse_arrow_body()
                return AsyncArrowFunc([Param(n)],b)
            return Identifier(n)
        return Literal('undefined')

    def parse_params(self):
        self.expect(TT_LPAREN); ps=[]
        while self.cur().type!=TT_RPAREN:
            rest=False
            if self.cur().type==TT_SPREAD: self.adv(); rest=True
            n=self.expect(TT_IDENT).value
            df=None
            if self.match(TT_OP,'='): df=self.parse_assign_expr()
            ps.append(Param(n,rest=rest,default=df)); self.match(TT_COMMA)
        self.expect(TT_RPAREN); return ps

    def parse_return(self):
        self.adv(); v=None
        if self.cur().type not in (TT_SEMI,TT_EOF,TT_RBRACE):
            v=self.parse_expr()
        self.skips(); return ReturnStmt(v)

    def parse_switch(self):
        self.adv(); self.expect(TT_LPAREN)
        d=self.parse_expr(); self.expect(TT_RPAREN)
        self.expect(TT_LBRACE); cases=[]
        while self.cur().type!=TT_RBRACE:
            if self.cur().type==TT_KEYWORD and self.cur().value=='case':
                self.adv(); t=self.parse_expr(); self.expect(TT_COLON)
            elif self.cur().type==TT_KEYWORD and self.cur().value=='default':
                self.adv(); self.expect(TT_COLON); t=None
            else: break
            cons=[]
            while self.cur().type not in (TT_EOF,TT_RBRACE) and \
                  not (self.cur().type==TT_KEYWORD and self.cur().value in ('case','default')):
                s=self.parse_stmt()
                if s: cons.append(s)
            cases.append(SwitchCase(t,cons))
        self.expect(TT_RBRACE); return SwitchStmt(d,cases)

    def parse_throw(self):
        self.adv(); a=self.parse_expr(); self.skips()
        return ThrowStmt(a)

    def parse_try(self):
        self.adv(); block=self.parse_block()
        handler=None; finalizer=None
        if self.cur().type==TT_KEYWORD and self.cur().value=='catch':
            self.adv(); cp=None
            if self.cur().type==TT_LPAREN:
                self.adv(); cp=self.expect(TT_IDENT).value; self.expect(TT_RPAREN)
            cb=self.parse_block(); handler=(cp,cb)
        if self.cur().type==TT_KEYWORD and self.cur().value=='finally':
            self.adv(); finalizer=self.parse_block()
        return TryCatch(block,handler,finalizer)

    def parse_expr(self): return self.parse_assign_expr()

    def parse_assign_expr(self):
        l=self.parse_ternary()
        ops={'=','+=','-=','*=','/=','%=','**='}
        if self.cur().type==TT_OP and self.cur().value in ops:
            op=self.adv().value; r=self.parse_assign_expr()
            return AssignExpr(op,l,r)
        return l

    def parse_ternary(self):
        t=self.parse_or()
        if self.match(TT_QUESTION):
            c=self.parse_assign_expr(); self.expect(TT_COLON); a=self.parse_assign_expr()
            return TernaryExpr(t,c,a)
        return t

    def parse_or(self):
        l=self.parse_and()
        while self.cur().type==TT_OP and self.cur().value in ('||','??'):
            op=self.adv().value; r=self.parse_and(); l=BinOp(op,l,r)
        return l

    def parse_and(self):
        l=self.parse_eq()
        while self.cur().type==TT_OP and self.cur().value=='&&':
            self.adv(); r=self.parse_eq(); l=BinOp('&&',l,r)
        return l

    def parse_eq(self):
        l=self.parse_rel()
        while self.cur().type==TT_OP and self.cur().value in ('==','!=','===','!=='):
            op=self.adv().value; r=self.parse_rel(); l=BinOp(op,l,r)
        return l

    def parse_rel(self):
        l=self.parse_add()
        while self.cur().type==TT_OP and self.cur().value in ('<','>','<=','>='):
            op=self.adv().value; r=self.parse_add(); l=BinOp(op,l,r)
        return l

    def parse_add(self):
        l=self.parse_mul()
        while self.cur().type==TT_OP and self.cur().value in ('+','-'):
            op=self.adv().value; r=self.parse_mul(); l=BinOp(op,l,r)
        return l

    def parse_mul(self):
        l=self.parse_exp()
        while self.cur().type==TT_OP and self.cur().value in ('*','/','%'):
            op=self.adv().value; r=self.parse_exp(); l=BinOp(op,l,r)
        return l

    def parse_exp(self):
        l=self.parse_unary()
        if self.cur().type==TT_OP and self.cur().value=='**':
            self.adv(); r=self.parse_exp(); return BinOp('**',l,r)
        return l

    def parse_unary(self):
        if self.cur().type==TT_OP and self.cur().value=='!':
            self.adv(); return UnaryOp('!',self.parse_unary())
        if self.cur().type==TT_OP and self.cur().value=='-':
            self.adv(); return UnaryOp('-',self.parse_unary())
        if self.cur().type==TT_OP and self.cur().value=='+':
            self.adv(); return UnaryOp('+',self.parse_unary())
        if self.cur().type==TT_KEYWORD and self.cur().value=='typeof':
            self.adv(); return TypeofExpr(self.parse_unary())
        if self.cur().type==TT_KEYWORD and self.cur().value=='await':
            self.adv(); return AwaitExpr(self.parse_unary())
        if self.cur().type==TT_OP and self.cur().value=='++':
            self.adv(); return UnaryOp('++',self.parse_postfix(),pre=True)
        if self.cur().type==TT_OP and self.cur().value=='--':
            self.adv(); return UnaryOp('--',self.parse_postfix(),pre=True)
        return self.parse_postfix()

    def parse_postfix(self):
        e=self.parse_call_member()
        if self.cur().type==TT_OP and self.cur().value in ('++','--'):
            op=self.adv().value; return UnaryOp(op,e,pre=False)
        return e

    def parse_call_member(self):
        obj=self.parse_primary()
        while True:
            if self.cur().type==TT_DOT:
                self.adv(); p=self.adv().value; obj=MemberExpr(obj,p,False)
            elif self.cur().type==TT_LBRACKET:
                self.adv(); p=self.parse_expr(); self.expect(TT_RBRACKET)
                obj=MemberExpr(obj,p,True)
            elif self.cur().type==TT_LPAREN:
                obj=CallExpr(obj,self.parse_args())
            else: break
        return obj

    def parse_args(self):
        self.expect(TT_LPAREN); args=[]
        while self.cur().type!=TT_RPAREN:
            if self.cur().type==TT_SPREAD:
                self.adv(); args.append(SpreadElement(self.parse_assign_expr()))
            else: args.append(self.parse_assign_expr())
            self.match(TT_COMMA)
        self.expect(TT_RPAREN); return args

    def parse_arrow_body(self):
        if self.cur().type==TT_LBRACE: return self.parse_block()
        return self.parse_assign_expr()

    def parse_primary(self):
        t=self.cur()
        if t.type==TT_NUMBER: self.adv(); return Literal(t.value)
        if t.type==TT_STRING: self.adv(); return Literal(t.value)
        if t.type==TT_BOOL:   self.adv(); return Literal(t.value)
        if t.type==TT_NULL:   self.adv(); return Literal(None)
        if t.type==TT_UNDEF:  self.adv(); return Literal('undefined')
        if t.type==TT_TEMPLATE: self.adv(); return self.parse_template(t.value)

        if t.type==TT_KEYWORD and t.value=='async':
            self.adv()
            if self.cur().type==TT_KEYWORD and self.cur().value=='function':
                self.adv()
                n=None
                if self.cur().type==TT_IDENT: n=self.adv().value
                p=self.parse_params(); b=self.parse_block()
                return AsyncFuncExpr(n,p,b)
            return self.parse_async_arrow()

        if t.type==TT_KEYWORD and t.value=='await':
            self.adv(); a=self.parse_unary(); return AwaitExpr(a)

        if t.type==TT_KEYWORD and t.value=='new':
            self.adv(); c=self.parse_call_member()
            a=self.parse_args() if self.cur().type==TT_LPAREN else []
            return NewExpr(c,a)

        if t.type==TT_KEYWORD and t.value=='function':
            self.adv()
            n=None
            if self.cur().type==TT_IDENT: n=self.adv().value
            p=self.parse_params(); b=self.parse_block()
            return FuncExpr(n,p,b)

        if t.type==TT_IDENT:
            self.adv()
            if self.cur().type==TT_ARROW:
                self.adv(); b=self.parse_arrow_body()
                return ArrowFunc([Param(t.value)],b)
            return Identifier(t.value)

        if t.type==TT_LPAREN:
            self.adv()
            if self.cur().type==TT_RPAREN:
                self.adv(); self.expect(TT_ARROW); b=self.parse_arrow_body()
                return ArrowFunc([],b)
            e=self.parse_assign_expr()
            if self.cur().type==TT_COMMA:
                ps=[e]
                while self.match(TT_COMMA):
                    if self.cur().type==TT_SPREAD:
                        self.adv(); ps.append(SpreadElement(self.parse_assign_expr()))
                    else: ps.append(self.parse_assign_expr())
                self.expect(TT_RPAREN)
                if self.cur().type==TT_ARROW:
                    self.adv()
                    pl=[]
                    for p in ps:
                        if isinstance(p,Identifier): pl.append(Param(p.name))
                        elif isinstance(p,SpreadElement) and isinstance(p.argument,Identifier):
                            pl.append(Param(p.argument.name,rest=True))
                    return ArrowFunc(pl,self.parse_arrow_body())
            self.expect(TT_RPAREN)
            if self.cur().type==TT_ARROW:
                self.adv()
                if isinstance(e,Identifier):
                    return ArrowFunc([Param(e.name)],self.parse_arrow_body())
            return e

        if t.type==TT_LBRACKET:
            self.adv(); els=[]
            while self.cur().type!=TT_RBRACKET:
                if self.cur().type==TT_SPREAD:
                    self.adv(); els.append(SpreadElement(self.parse_assign_expr()))
                else: els.append(self.parse_assign_expr())
                self.match(TT_COMMA)
            self.expect(TT_RBRACKET); return ArrayExpr(els)

        if t.type==TT_LBRACE: return self.parse_object()
        raise ThrowSignal(JSSyntaxError(f"Unexpected token '{self._tv(t)}'"))

    def parse_object(self):
        self.expect(TT_LBRACE); props=[]
        while self.cur().type!=TT_RBRACE:
            if self.cur().type==TT_SPREAD:
                self.adv(); props.append(SpreadElement(self.parse_assign_expr()))
                self.match(TT_COMMA); continue
            if self.cur().type in (TT_IDENT,TT_STRING,TT_NUMBER,TT_KEYWORD):
                k=self.adv().value
            else: k=self.adv().value
            if self.cur().type==TT_LPAREN:
                p=self.parse_params(); b=self.parse_block()
                props.append(Property(k,FuncExpr(k,p,b)))
            elif self.match(TT_COLON):
                props.append(Property(k,self.parse_assign_expr()))
            else:
                props.append(Property(k,Identifier(str(k))))
            self.match(TT_COMMA)
        self.expect(TT_RBRACE); return ObjectExpr(props)

    def parse_template(self,raw):
        parts=re.split(r'\$\{',raw)
        if len(parts)==1: return Literal(raw)
        exprs=[]; proc=[parts[0]]
        for part in parts[1:]:
            idx=part.find('}')
            if idx!=-1:
                es=part[:idx]; rest=part[idx+1:]
                l=Lexer(es); toks=l.tokenize()
                p=Parser(toks); exprs.append(p.parse_expr())
                proc.append(rest)
        return TemplateLiteral(proc,exprs)

# ═══════════════════════════════════════════
#  INTERPRETER
# ═══════════════════════════════════════════
class Interpreter:
    def __init__(self):
        self.global_env=Environment()
        self._microtask_queue=[]
        self._macrotask_queue=[]
        self._timer_id=0
        self._cancelled_timers=set()
        self._setup_globals()

    def _setup_globals(self):
        env=self.global_env
        env.define('undefined','undefined')
        env.define('NaN',float('nan'))
        env.define('Infinity',float('inf'))
        env.define('console',{
            'log':self._console_log,'error':self._console_log,'warn':self._console_log,
            'info':self._console_log,'dir':self._console_log,
        })
        env.define('Math',{
            'floor':lambda *a:int(math.floor(a[0])),'ceil':lambda *a:int(math.ceil(a[0])),
            'round':lambda *a:int(round(a[0])),'abs':lambda *a:abs(a[0]),
            'max':lambda *a:max(a),'min':lambda *a:min(a),
            'sqrt':lambda *a:math.sqrt(a[0]),'pow':lambda *a:a[0]**a[1],
            'random':lambda *a:random.random(),'log':lambda *a:math.log(a[0]),
            'log2':lambda *a:math.log2(a[0]),'log10':lambda *a:math.log10(a[0]),
            'trunc':lambda *a:int(a[0]),'sign':lambda *a:(1 if a[0]>0 else -1 if a[0]<0 else 0),
            'PI':math.pi,'E':math.e,'LN2':math.log(2),'LN10':math.log(10),
            'hypot':lambda *a:math.hypot(*a),'sin':lambda *a:math.sin(a[0]),
            'cos':lambda *a:math.cos(a[0]),'tan':lambda *a:math.tan(a[0]),
        })
        env.define('Number',self._Number)
        env.define('String',self._String)
        env.define('Boolean',self._Boolean)
        env.define('parseInt',lambda *a:self._parseInt(*a))
        env.define('parseFloat',lambda *a:self._parseFloat(*a))
        env.define('isNaN',lambda *a:a[0]!=a[0] if isinstance(a[0],float) else False)
        env.define('isFinite',lambda *a:math.isfinite(a[0]) if isinstance(a[0],(int,float)) else False)
        env.define('Array',{'isArray':lambda *a:isinstance(a[0],list),'from':lambda *a:list(a[0]) if a else []})
        env.define('Object',{
            'keys':lambda *a:list(a[0].keys()) if isinstance(a[0],dict) else [],
            'values':lambda *a:list(a[0].values()) if isinstance(a[0],dict) else [],
            'entries':lambda *a:[[k,v] for k,v in a[0].items()] if isinstance(a[0],dict) else [],
            'assign':self._obj_assign,'freeze':lambda *a:a[0],'create':lambda *a:{},
        })
        env.define('JSON',{'stringify':self._json_str,'parse':self._json_parse})
        env.define('Date',self._DateCtor)
        env.define('Promise',self._make_promise_ctor())
        env.define('setTimeout',self._setTimeout)
        env.define('clearTimeout',lambda *a:self._cancelled_timers.add(int(a[0])) if a else None)
        env.define('setInterval',self._setInterval)
        env.define('clearInterval',lambda *a:self._cancelled_timers.add(int(a[0])) if a else None)
        env.define('queueMicrotask',lambda *a:self._microtask_queue.append((a[0],[])) if a else None)
        # Task 2 & 3: Map and Set constructors
        env.define('Map', self._make_map_ctor())
        env.define('Set', self._make_set_ctor())
        # JS Error constructors
        env.define('Error', lambda *a: JSError('Error', str(a[0]) if a else ''))
        env.define('TypeError', lambda *a: JSTypeError(str(a[0]) if a else ''))
        env.define('ReferenceError', lambda *a: JSReferenceError(str(a[0]) if a else ''))
        env.define('SyntaxError', lambda *a: JSSyntaxError(str(a[0]) if a else ''))
        env.define('RangeError', lambda *a: JSRangeError(str(a[0]) if a else ''))

    # ── Map constructor ──────────────────────
    def _make_map_ctor(self):
        interp=self
        def MapCtor(*a):
            init=a[0] if a else None
            m=JSMap(interp,init)
            return m
        return MapCtor

    # ── Set constructor ──────────────────────
    def _make_set_ctor(self):
        interp=self
        def SetCtor(*a):
            init=a[0] if a else None
            s=JSSet(interp,init)
            return s
        return SetCtor

    # ── console (Task 5) ─────────────────────
    def _console_log(self,*args):
        print(' '.join(self._disp(a) for a in args))

    def _disp(self,v):
        if v is None: return 'null'
        if v=='undefined': return 'undefined'
        # Task 5: JSError display
        if isinstance(v,JSError): return str(v)
        # Task 5: JSPromise display
        if isinstance(v,JSPromise):
            if v.state==JSPromise.FULFILLED: return f'Promise {{ {self._disp(v.value)} }}'
            if v.state==JSPromise.REJECTED:  return f'Promise {{ <rejected> {self._disp(v.reason)} }}'
            return 'Promise { <pending> }'
        # Task 5: JSMap display
        if isinstance(v,JSMap):
            n=len(v._keys)
            inner=', '.join(f'{self._disp(k)} => {self._disp(val)}' for k,val in zip(v._keys,v._vals))
            return f'Map({n}) {{ {inner} }}'
        # Task 5: JSSet display
        if isinstance(v,JSSet):
            n=len(v._items)
            inner=', '.join(self._disp(x) for x in v._items)
            return f'Set({n}) {{ {inner} }}'
        if isinstance(v,bool): return 'true' if v else 'false'
        if isinstance(v,float):
            if v!=v: return 'NaN'
            if v==float('inf'): return 'Infinity'
            if v==float('-inf'): return '-Infinity'
            if v==int(v): return str(int(v))
            return str(v)
        if isinstance(v,int): return str(v)
        if isinstance(v,str): return v
        if isinstance(v,list): return '['+', '.join(self._disp(x) for x in v)+']'
        if isinstance(v,dict):
            if not v: return '{}'
            inner=', '.join(f'{k}: {self._disp(val)}' for k,val in v.items())
            return '{ '+inner+' }'
        if callable(v) or isinstance(v,JSFunction): return '[Function]'
        return str(v)

    def _js_str(self,v):
        if v is None: return 'null'
        if v=='undefined': return 'undefined'
        if isinstance(v,bool): return 'true' if v else 'false'
        if isinstance(v,JSError): return str(v)
        if isinstance(v,float):
            if v!=v: return 'NaN'
            if v==float('inf'): return 'Infinity'
            if v==float('-inf'): return '-Infinity'
            if v==int(v): return str(int(v))
            return str(v)
        if isinstance(v,int): return str(v)
        if isinstance(v,str): return v
        if isinstance(v,list): return ','.join(self._js_str(x) for x in v)
        if isinstance(v,dict): return '[object Object]'
        return str(v)

    def _num(self,v):
        if isinstance(v,bool): return 1 if v else 0
        if isinstance(v,(int,float)): return v
        if isinstance(v,str):
            s=v.strip()
            if s=='': return 0
            try: return int(s)
            except:
                try: return float(s)
                except: return float('nan')
        if v is None: return 0
        if v=='undefined': return float('nan')
        return float('nan')

    def _bool(self, v):
        if v == 'undefined':
            return False

        if v is None:
            return False

        if isinstance(v, bool):
            return v

        if isinstance(v, (int, float)):
            return v != 0 and v == v

        if isinstance(v, str):
            return len(v) > 0

        if isinstance(v, (list, dict)):
            return True

        if isinstance(v, (JSPromise, JSMap, JSSet)):
            return True

        return bool(v)    

    def _Number(self,*a): return self._num(a[0]) if a else 0
    def _String(self,*a): return self._js_str(a[0]) if a else ''
    def _Boolean(self,*a): return self._bool(a[0]) if a else False

    def _parseInt(self,*a):
        if not a: return float('nan')
        s=self._js_str(a[0]).strip(); base=int(a[1]) if len(a)>1 else 10
        try: return int(s,base)
        except:
            s2=''
            for c in s:
                if c.isdigit() or (c=='-' and not s2): s2+=c
                else: break
            try: return int(s2) if s2 and s2!='-' else float('nan')
            except: return float('nan')

    def _parseFloat(self,*a):
        if not a: return float('nan')
        s=self._js_str(a[0]).strip()
        try: return float(s)
        except: return float('nan')

    def _obj_assign(self,*a):
        t=a[0] if a else {}
        for s in a[1:]:
            if isinstance(s,dict): t.update(s)
        return t

    def _json_str(self,*a):
        import json
        def conv(v):
            if isinstance(v,bool): return v
            if isinstance(v,list): return [conv(x) for x in v]
            if isinstance(v,dict): return {k:conv(vv) for k,vv in v.items()}
            if v=='undefined': return None
            return v
        return json.dumps(conv(a[0])) if a else 'undefined'

    def _json_parse(self,*a):
        import json
        return json.loads(a[0]) if a else 'undefined'

    def _DateCtor(self,*a):
        now=datetime.datetime.now()
        return {
            'getFullYear':lambda *_:now.year,'getMonth':lambda *_:now.month-1,
            'getDate':lambda *_:now.day,'getDay':lambda *_:now.weekday(),
            'getHours':lambda *_:now.hour,'getMinutes':lambda *_:now.minute,
            'getSeconds':lambda *_:now.second,'getMilliseconds':lambda *_:now.microsecond//1000,
            'getTime':lambda *_:int(now.timestamp()*1000),
            'toLocaleDateString':lambda *_:now.strftime('%m/%d/%Y'),
            'toLocaleTimeString':lambda *_:now.strftime('%H:%M:%S'),
            'toISOString':lambda *_:now.isoformat()+'Z',
            'toString':lambda *_:now.strftime('%a %b %d %Y %H:%M:%S'),
        }

    def _make_promise_ctor(self):
        interp=self
        def PromiseCtor(*a):
            executor=a[0] if a else None
            p=JSPromise(interp)
            def _res(*x): p.resolve(x[0] if x else 'undefined')
            def _rej(*x): p.reject(x[0] if x else 'undefined')
            if executor:
                try:
                    if isinstance(executor,JSFunction): interp._call_fn(executor,[_res,_rej])
                    elif callable(executor): executor(_res,_rej)
                except ThrowSignal as e: p.reject(e.value)
                except Exception as e: p.reject(str(e))
            return p

        def _resolve(*a):
            v=a[0] if a else 'undefined'
            if isinstance(v,JSPromise): return v
            p=JSPromise(interp); p.resolve(v); return p

        def _reject(*a):
            p=JSPromise(interp); p.reject(a[0] if a else 'undefined'); return p

        def _all(*a):
            ps=a[0] if a and isinstance(a[0],list) else []
            rp=JSPromise(interp)
            if not ps: rp.resolve([]); return rp
            res=['undefined']*len(ps); done=[0]
            def mk(i):
                def on_f(v): res[i]=v; done[0]+=1; (rp.resolve(res[:]) if done[0]==len(ps) else None)
                return on_f
            for i,p in enumerate(ps):
                if isinstance(p,JSPromise): p._add_then(mk(i),rp.reject)
                else: mk(i)(p)
            return rp

        def _allSettled(*a):
            ps=a[0] if a and isinstance(a[0],list) else []
            rp=JSPromise(interp)
            if not ps: rp.resolve([]); return rp
            res=[None]*len(ps); done=[0]
            def mk(i):
                def f(v): res[i]={'status':'fulfilled','value':v}; done[0]+=1; (rp.resolve(res[:]) if done[0]==len(ps) else None)
                def r(v): res[i]={'status':'rejected','reason':v}; done[0]+=1; (rp.resolve(res[:]) if done[0]==len(ps) else None)
                return f,r
            for i,p in enumerate(ps):
                f,r=mk(i)
                if isinstance(p,JSPromise): p._add_then(f,r)
                else: f(p)
            return rp

        def _race(*a):
            ps=a[0] if a and isinstance(a[0],list) else []
            rp=JSPromise(interp); settled=[False]
            def mk(fn):
                def handler(v):
                    if not settled[0]: settled[0]=True; fn(v)
                return handler
            for p in ps:
                if isinstance(p,JSPromise): p._add_then(mk(rp.resolve),mk(rp.reject))
                elif not settled[0]: settled[0]=True; rp.resolve(p)
            return rp

        def _any(*a):
            ps=a[0] if a and isinstance(a[0],list) else []
            rp=JSPromise(interp)
            if not ps: rp.reject('All promises were rejected'); return rp
            errs=['undefined']*len(ps); rej=[0]
            def mk(i):
                def f(v): rp.resolve(v)
                def r(v): errs[i]=v; rej[0]+=1; (rp.reject(errs[:]) if rej[0]==len(ps) else None)
                return f,r
            for i,p in enumerate(ps):
                f,r=mk(i)
                if isinstance(p,JSPromise): p._add_then(f,r)
                else: f(p)
            return rp

        PromiseCtor.resolve=_resolve; PromiseCtor.reject=_reject
        PromiseCtor.all=_all; PromiseCtor.allSettled=_allSettled
        PromiseCtor.race=_race; PromiseCtor.any=_any
        return PromiseCtor

    def _setTimeout(self,*a):
        cb=a[0] if a else None
        delay_ms=a[1] if len(a)>1 else 0
        cb_args=list(a[2:]) if len(a)>2 else []
        self._timer_id+=1; tid=self._timer_id
        delay_s=(delay_ms/1000.0) if isinstance(delay_ms,(int,float)) and delay_ms>0 else 0
        due=time.monotonic()+delay_s
        self._macrotask_queue.append((due,tid,cb,cb_args,None))
        self._macrotask_queue.sort(key=lambda x:(x[0],x[1]))
        return tid

    def _setInterval(self,*a):
        cb=a[0] if a else None
        interval_ms=a[1] if len(a)>1 else 0
        cb_args=list(a[2:]) if len(a)>2 else []
        self._timer_id+=1; tid=self._timer_id
        iv=max(0,interval_ms if isinstance(interval_ms,(int,float)) else 0)
        due=time.monotonic()+iv/1000.0
        self._macrotask_queue.append((due,tid,cb,cb_args,iv))
        self._macrotask_queue.sort(key=lambda x:(x[0],x[1]))
        return tid

    def _drain_micro(self):
        iters=0
        while self._microtask_queue and iters<10000:
            cb,args=self._microtask_queue.pop(0)
            try:
                if isinstance(cb,JSFunction): self._call_fn(cb,args)
                elif callable(cb): cb(*args)
            except (ReturnSignal,ThrowSignal): pass
            iters+=1

    def _drain_until(self,promise,max_iter=10000):
        iters=0
        while promise.state==JSPromise.PENDING and iters<max_iter:
            self._drain_micro()
            if self._macrotask_queue and promise.state==JSPromise.PENDING:
                due,tid,cb,cb_args,iv=self._macrotask_queue.pop(0)
                now=time.monotonic()
                if due>now: time.sleep(due-now)
                if tid not in self._cancelled_timers:
                    try:
                        if cb:
                            if isinstance(cb,JSFunction): self._call_fn(cb,cb_args)
                            elif callable(cb): cb(*cb_args)
                    except (ReturnSignal,ThrowSignal): pass
                    if iv is not None:
                        new_due=time.monotonic()+iv/1000.0
                        self._macrotask_queue.append((new_due,tid,cb,cb_args,iv))
                        self._macrotask_queue.sort(key=lambda x:(x[0],x[1]))
            iters+=1

    def _run_loop(self):
        iters=0
        while (self._microtask_queue or self._macrotask_queue) and iters<100000:
            self._drain_micro()
            if self._macrotask_queue:
                due,tid,cb,cb_args,iv=self._macrotask_queue.pop(0)
                now=time.monotonic()
                if due>now: time.sleep(due-now)
                if tid not in self._cancelled_timers:
                    try:
                        if cb:
                            if isinstance(cb,JSFunction): self._call_fn(cb,cb_args)
                            elif callable(cb): cb(*cb_args)
                    except (ReturnSignal,ThrowSignal): pass
                    if iv is not None:
                        new_due=time.monotonic()+iv/1000.0
                        self._macrotask_queue.append((new_due,tid,cb,cb_args,iv))
                        self._macrotask_queue.sort(key=lambda x:(x[0],x[1]))
                self._drain_micro()
            iters+=1

    def _typeof(self,v):
        if v is None: return 'object'
        if v=='undefined': return 'undefined'
        if isinstance(v,bool): return 'boolean'
        if isinstance(v,(int,float)): return 'number'
        if isinstance(v,str): return 'string'
        if isinstance(v,(list,dict,JSMap,JSSet)): return 'object'
        if isinstance(v,JSPromise): return 'object'
        if callable(v) or isinstance(v,JSFunction): return 'function'
        return 'undefined'

    def _seq(self,a,b):
        if isinstance(a,(int,float)) and isinstance(b,(int,float)): return a==b
        if type(a)!=type(b): return False
        return a==b

    def _leq(self,a,b):
        if a is None and b is None: return True
        if a is None and b=='undefined': return True
        if a=='undefined' and b is None: return True
        if a=='undefined' and b=='undefined': return True
        if isinstance(a,bool): a=int(a)
        if isinstance(b,bool): b=int(b)
        if isinstance(a,(int,float)) and isinstance(b,str):
            try: return a==float(b)
            except: return False
        if isinstance(a,str) and isinstance(b,(int,float)):
            try: return float(a)==b
            except: return False
        return a==b

    # ═══════════════════════════════════════
    #  EXEC
    # ═══════════════════════════════════════
    def exec(self,program,env=None):
        if env is None: env=self.global_env
        for s in program.body:
            if isinstance(s,FuncDecl):
                fn=JSFunction(s.name,s.params,s.body,env)
                env.define(s.name,fn)
        for s in program.body:
            if not isinstance(s,FuncDecl):
                self.exec_stmt(s,env)
        self._run_loop()

    def exec_stmt(self,node,env):
        if isinstance(node,VarDecl):
            for d in node.declarations:
                if d.is_destructure:
                    v=self.eval(d.init,env) if d.init else 'undefined'
                    if d.is_array_dest:
                        for i,k in enumerate(d.keys):
                            if k is not None:
                                env.define_let(k,v[i] if isinstance(v,list) and i<len(v) else 'undefined',node.kind)
                    else:
                        for ok,ak in d.keys:
                            env.define_let(ak,v.get(ok,'undefined') if isinstance(v,dict) else 'undefined',node.kind)
                else:
                    v='undefined'
                    if d.init:
                        try:
                            v=self.eval(d.init,env)
                        except AwaitSuspend as aws:
                            _n=d.name; _k=node.kind; _e=env
                            def _def(val,n=_n,k=_k,e=_e):
                                if k=='var': e.define(n,val)
                                else: e.define_let(n,val,k)
                            raise AwaitSuspend(aws.promise,_def)
                    if node.kind=='var': env.define(d.name,v)
                    else: env.define_let(d.name,v,node.kind)

        elif isinstance(node,ExprStmt): self.eval(node.expr,env)
        elif isinstance(node,IfStmt):
            if self._bool(self.eval(node.test,env)): self.exec_stmt(node.consequent,env)
            elif node.alternate: self.exec_stmt(node.alternate,env)
        elif isinstance(node,BlockStmt):
            be=Environment(env)
            for s in node.body: self.exec_stmt(s,be)
        elif isinstance(node,WhileStmt):
            while self._bool(self.eval(node.test,env)):
                try: self.exec_stmt(node.body,Environment(env))
                except BreakSignal: break
                except ContinueSignal: continue
        elif isinstance(node,DoWhileStmt):
            while True:
                try: self.exec_stmt(node.body,Environment(env))
                except BreakSignal: break
                except ContinueSignal: pass
                if not self._bool(self.eval(node.test,env)): break
        elif isinstance(node,ForStmt):
            le=Environment(env)
            if node.init: self.exec_stmt(node.init,le)
            while True:
                if node.test and not self._bool(self.eval(node.test,le)): break
                try: self.exec_stmt(node.body,Environment(le))
                except BreakSignal: break
                except ContinueSignal: pass
                if node.update: self.eval(node.update,le)
        elif isinstance(node,ForOfStmt):
            it=self.eval(node.iterable,env)
            # Task 4: Map/Set iteration
            if isinstance(it,JSSet): items=list(it._items)
            elif isinstance(it,JSMap): items=list(it._entries_iter())
            elif isinstance(it,(list,str)): items=list(it)
            elif it and hasattr(it,'__iter__'): items=list(it)
            else: raise ThrowSignal(JSTypeError(f'{self._disp(it)} is not iterable'))
            for item in items:
                ie=Environment(env); ie.define(node.var,item)
                try: self.exec_stmt(node.body,ie)
                except BreakSignal: break
                except ContinueSignal: continue
        elif isinstance(node,ForInStmt):
            obj=self.eval(node.obj,env)
            keys=list(obj.keys()) if isinstance(obj,dict) else [str(i) for i in range(len(obj))] if isinstance(obj,list) else []
            for k in keys:
                ie=Environment(env); ie.define(node.var,k)
                try: self.exec_stmt(node.body,ie)
                except BreakSignal: break
                except ContinueSignal: continue
        elif isinstance(node,FuncDecl):
            fn=JSFunction(node.name,node.params,node.body,env)
            env.define(node.name,fn)
        elif isinstance(node,ReturnStmt):
            v=self.eval(node.value,env) if node.value else 'undefined'
            raise ReturnSignal(v)
        elif isinstance(node,SwitchStmt):
            disc=self.eval(node.discriminant,env); matched=False
            try:
                for case in node.cases:
                    if not matched:
                        if case.test is None: matched=True
                        elif self._seq(disc,self.eval(case.test,env)): matched=True
                    if matched:
                        try:
                            for s in case.consequent: self.exec_stmt(s,env)
                        except BreakSignal: return
            except BreakSignal: pass
        elif isinstance(node,BreakStmt): raise BreakSignal()
        elif isinstance(node,ContinueStmt): raise ContinueSignal()
        elif isinstance(node,ThrowStmt):
            raise ThrowSignal(self.eval(node.argument,env))
        elif isinstance(node,TryCatch):
            try:
                be=Environment(env)
                for s in node.block.body: self.exec_stmt(s,be)
            except AwaitSuspend: raise   # ← ADD THIS LINE
            except ThrowSignal as e:
                if node.handler:
                    cp,cb=node.handler; ce=Environment(env)
                    if cp: ce.define(cp,e.value)
                    for s in cb.body: self.exec_stmt(s,ce)
            except Exception as e:
                if node.handler:
                    cp,cb=node.handler; ce=Environment(env)
                    if cp: ce.define(cp,str(e))
                    for s in cb.body: self.exec_stmt(s,ce)
            finally:
                if node.finalizer:
                    fe=Environment(env)
                    for s in node.finalizer.body: self.exec_stmt(s,fe)

    # ═══════════════════════════════════════
    #  EVAL
    # ═══════════════════════════════════════
    def eval(self,node,env):
        if isinstance(node,Literal): return node.value
        if isinstance(node,Identifier): return env.get(node.name)

        if isinstance(node,TemplateLiteral):
            r=node.raw[0]
            for i,e in enumerate(node.expressions):
                r+=self._js_str(self.eval(e,env))
                if i+1<len(node.raw): r+=node.raw[i+1]
            return r

        if isinstance(node,ArrayExpr):
            els=[]
            for el in node.elements:
                if isinstance(el,SpreadElement):
                    v=self.eval(el.argument,env)
                    # Task 4: spread Set/Map
                    if isinstance(v,JSSet): els.extend(v._items)
                    elif isinstance(v,JSMap): els.extend(v._entries_iter())
                    elif isinstance(v,list): els.extend(v)
                    elif isinstance(v,str): els.extend(list(v))
                else: els.append(self.eval(el,env))
            return els

        if isinstance(node,ObjectExpr):
            obj={}
            for p in node.properties:
                if isinstance(p,SpreadElement):
                    v=self.eval(p.argument,env)
                    if isinstance(v,dict): obj.update(v)
                else: obj[str(p.key)]=self.eval(p.value,env)
            return obj

        if isinstance(node,FuncExpr):
            return JSFunction(node.name,node.params,node.body,env)
        if isinstance(node,ArrowFunc):
            return JSFunction(None,node.params,node.body,env)
        if isinstance(node,AsyncFuncExpr):
            return JSFunction(node.name,node.params,node.body,env,is_async=True)
        if isinstance(node,AsyncArrowFunc):
            return JSFunction(None,node.params,node.body,env,is_async=True)

        if isinstance(node,AwaitExpr):
            v=self.eval(node.argument,env)
            if isinstance(v,JSPromise):
                raise AwaitSuspend(v)
            wp=JSPromise(self); wp.resolve(v)
            raise AwaitSuspend(wp)

        if isinstance(node,TypeofExpr):
            try: v=self.eval(node.operand,env)
            except: return 'undefined'
            return self._typeof(v)

        if isinstance(node,NewExpr):
            c=self.eval(node.callee,env)
            args=self._eval_args(node.args,env)
            if callable(c): return c(*args)
            return {}

        if isinstance(node,BinOp): return self.eval_bin(node,env)
        if isinstance(node,UnaryOp): return self.eval_unary(node,env)
        if isinstance(node,AssignExpr): return self.eval_assign(node,env)
        if isinstance(node,TernaryExpr):
            return self.eval(node.consequent if self._bool(self.eval(node.test,env)) else node.alternate,env)
        if isinstance(node,MemberExpr): return self.eval_member(node,env)
        if isinstance(node,CallExpr): return self.eval_call(node,env)
        return 'undefined'

    def eval_bin(self,node,env):
        op=node.op
        if op=='&&':
            l=self.eval(node.left,env); return l if not self._bool(l) else self.eval(node.right,env)
        if op=='||':
            l=self.eval(node.left,env); return l if self._bool(l) else self.eval(node.right,env)
        if op=='??':
            l=self.eval(node.left,env); return l if l is not None and l!='undefined' else self.eval(node.right,env)
        l=self.eval(node.left,env); r=self.eval(node.right,env)
        if op=='+':
            if isinstance(l,str) or isinstance(r,str): return self._js_str(l)+self._js_str(r)
            if isinstance(l,bool) and isinstance(r,bool): return int(l)+int(r)
            ln=self._num(l); rn=self._num(r)
            res=ln+rn
            return int(res) if isinstance(ln,int) and isinstance(rn,int) else res
        if op=='-':
            ln=self._num(l); rn=self._num(r); res=ln-rn
            return int(res) if isinstance(ln,int) and isinstance(rn,int) else res
        if op=='*':
            ln=self._num(l); rn=self._num(r); res=ln*rn
            return int(res) if isinstance(ln,int) and isinstance(rn,int) else res
        if op=='/':
            ln=self._num(l); rn=self._num(r)
            if rn==0: return float('inf') if ln>0 else float('-inf') if ln<0 else float('nan')
            res=ln/rn; return int(res) if res==int(res) and isinstance(ln,int) and isinstance(rn,int) else res
        if op=='%':
            ln=self._num(l); rn=self._num(r); return ln%rn
        if op=='**':
            ln=self._num(l); rn=self._num(r); res=ln**rn
            return int(res) if isinstance(res,float) and res==int(res) and rn>=0 else res
        if op=='===': return self._seq(l,r)
        if op=='!==': return not self._seq(l,r)
        if op=='==':  return self._leq(l,r)
        if op=='!=':  return not self._leq(l,r)
        ln=self._num(l); rn=self._num(r)
        if op=='<': return ln<rn
        if op=='>': return ln>rn
        if op=='<=': return ln<=rn
        if op=='>=': return ln>=rn
        return 'undefined'

    def eval_unary(self,node,env):
        op=node.op
        if op=='!': return not self._bool(self.eval(node.operand,env))
        if op=='-': return -self._num(self.eval(node.operand,env))
        if op=='+': return self._num(self.eval(node.operand,env))
        if op in ('++','--'):
            delta=1 if op=='++' else -1
            old=self._num(self._get_lv(node.operand,env))
            new=int(old+delta) if isinstance(old,int) else old+delta
            self._set_lv(node.operand,new,env)
            return old if not node.prefix else new
        return 'undefined'

    def _get_lv(self,node,env):
        if isinstance(node,Identifier): return env.get(node.name)
        if isinstance(node,MemberExpr): return self.eval_member(node,env)
        return 'undefined'

    def _set_lv(self,node,v,env):
        if isinstance(node,Identifier): env.set(node.name,v)
        elif isinstance(node,MemberExpr):
            obj=self.eval(node.obj,env)
            prop=node.prop if not node.computed else self._js_str(self.eval(node.prop,env))
            if isinstance(obj,list):
                idx=int(self._num(prop))
                while len(obj)<=idx: obj.append('undefined')
                obj[idx]=v
            elif isinstance(obj,dict): obj[str(prop)]=v
            elif isinstance(obj,JSMap): obj._set(prop,v)

    def eval_assign(self,node,env):
        op=node.op; r=self.eval(node.right,env)
        if op=='=': self._set_lv(node.left,r,env); return r
        old=self._get_lv(node.left,env)
        if op=='+=':
            nv=self._js_str(old)+self._js_str(r) if isinstance(old,str) or isinstance(r,str) else self._num(old)+self._num(r)
        elif op=='-=': nv=self._num(old)-self._num(r)
        elif op=='*=': nv=self._num(old)*self._num(r)
        elif op=='/=': nv=self._num(old)/self._num(r)
        elif op=='%=': nv=self._num(old)%self._num(r)
        elif op=='**=': nv=self._num(old)**self._num(r)
        else: nv=r
        self._set_lv(node.left,nv,env); return nv

    def eval_member(self,node,env,obj=None):
        if obj is None: obj=self.eval(node.obj,env)
        prop=node.prop if not node.computed else self._js_str(self.eval(node.prop,env))
        if obj is None:
            raise ThrowSignal(JSTypeError('Cannot read properties of null'))
        if obj=='undefined':
            raise ThrowSignal(JSTypeError('Cannot read properties of undefined'))

        # Promise
        if isinstance(obj,JSPromise):
            if prop=='then': return obj.then
            if prop=='catch': return obj.catch
            if prop=='finally': return obj.finally_
            return 'undefined'

        # Task 2: JSMap member access
        if isinstance(obj,JSMap):
            if prop=='size': return len(obj._keys)
            if prop=='set': return lambda *a:obj._set(a[0],a[1] if len(a)>1 else 'undefined')
            if prop=='get': return lambda *a:obj._get(a[0]) if a else 'undefined'
            if prop=='has': return lambda *a:obj._has(a[0]) if a else False
            if prop=='delete': return lambda *a:obj._delete(a[0]) if a else False
            if prop=='clear': return lambda *a:obj._clear()
            if prop=='keys': return lambda *a:obj._keys_iter()
            if prop=='values': return lambda *a:obj._vals_iter()
            if prop=='entries': return lambda *a:obj._entries_iter()
            if prop=='forEach': return lambda *a:obj._forEach(a[0]) if a else None
            return 'undefined'

        # Task 3: JSSet member access
        if isinstance(obj,JSSet):
            if prop=='size': return len(obj._items)
            if prop=='add': return lambda *a:obj._add(a[0]) if a else obj
            if prop=='has': return lambda *a:obj._has(a[0]) if a else False
            if prop=='delete': return lambda *a:obj._delete(a[0]) if a else False
            if prop=='clear': return lambda *a:obj._clear()
            if prop=='values': return lambda *a:obj._values()
            if prop=='keys': return lambda *a:obj._keys()
            if prop=='entries': return lambda *a:obj._entries()
            if prop=='forEach': return lambda *a:obj._forEach(a[0]) if a else None
            return 'undefined'

        # Array
        if isinstance(obj,list):
            if prop=='length': return len(obj)
            if prop=='push':    return lambda *a:(obj.extend(a),len(obj))[1]
            if prop=='pop':     return lambda *a:obj.pop() if obj else 'undefined'
            if prop=='shift':   return lambda *a:obj.pop(0) if obj else 'undefined'
            if prop=='unshift': return lambda *a:(obj.insert(0,a[-1]) or len(obj)) if a else len(obj)
            if prop=='reverse': return lambda *a:(obj.reverse() or obj)
            if prop=='join':    return lambda *a:self._arr_join(obj,a[0] if a else ',')
            if prop=='slice':   return lambda *a:self._arr_slice(obj,*a)
            if prop=='splice':  return lambda *a:self._arr_splice(obj,*a)
            if prop=='concat':  return lambda *a:obj+([x for aa in a for x in (list(aa) if isinstance(aa,list) else [aa])])
            if prop=='includes':return lambda *a:a[0] in obj if a else False
            if prop=='indexOf': return lambda *a:obj.index(a[0]) if a and a[0] in obj else -1
            if prop=='lastIndexOf': return lambda *a:len(obj)-1-obj[::-1].index(a[0]) if a and a[0] in obj else -1
            if prop=='findIndex':return lambda *a:self._find_idx(obj,a[0])
            if prop=='sort':    return lambda *a:self._arr_sort(obj,a[0] if a else None)
            if prop=='map':     return lambda *a:self._arr_map(obj,a[0])
            if prop=='filter':  return lambda *a:self._arr_filter(obj,a[0])
            if prop=='reduce':  return lambda *a:self._arr_reduce(obj,a[0],a[1] if len(a)>1 else None)
            if prop=='reduceRight': return lambda *a:self._arr_reduce(list(reversed(obj)),a[0],a[1] if len(a)>1 else None)
            if prop=='find':    return lambda *a:self._arr_find(obj,a[0])
            if prop=='some':    return lambda *a:self._arr_some(obj,a[0])
            if prop=='every':   return lambda *a:self._arr_every(obj,a[0])
            if prop=='flat':    return lambda *a:self._arr_flat(obj,int(a[0]) if a else 1)
            if prop=='flatMap': return lambda *a:self._arr_flatmap(obj,a[0])
            if prop=='forEach': return lambda *a:self._arr_foreach(obj,a[0])
            if prop=='fill':    return lambda *a:self._arr_fill(obj,*a)
            if prop=='toString':return lambda *a:self._arr_join(obj,',')
            if prop=='entries': return lambda *a:[[i,v] for i,v in enumerate(obj)]
            if prop=='keys':    return lambda *a:list(range(len(obj)))
            if prop=='values':  return lambda *a:list(obj)
            if prop=='at':      return lambda *a:obj[int(a[0]) if a[0]>=0 else len(obj)+int(a[0])] if a and -len(obj)<=int(a[0])<len(obj) else 'undefined'
            try:
                idx=int(prop)
                if idx<0: idx=len(obj)+idx
                return obj[idx] if 0<=idx<len(obj) else 'undefined'
            except: pass
            return 'undefined'

        # String
        if isinstance(obj,str):
            if prop=='length':      return len(obj)
            if prop=='toUpperCase': return lambda *a:obj.upper()
            if prop=='toLowerCase': return lambda *a:obj.lower()
            if prop=='trim':        return lambda *a:obj.strip()
            if prop=='trimStart':   return lambda *a:obj.lstrip()
            if prop=='trimEnd':     return lambda *a:obj.rstrip()
            if prop=='split':
                def do_split(*a):
                    if not a: return [obj]
                    sep=a[0]; lim=int(a[1]) if len(a)>1 else None
                    if sep=='': r=list(obj)
                    elif sep is None: r=obj.split()
                    else: r=obj.split(sep)
                    return r[:lim] if lim is not None else r
                return do_split
            if prop=='includes':    return lambda *a:(a[0] in obj) if a else False
            if prop=='startsWith':  return lambda *a:obj.startswith(a[0]) if a else False
            if prop=='endsWith':    return lambda *a:obj.endswith(a[0]) if a else False
            if prop=='indexOf':     return lambda *a:obj.find(a[0]) if a else -1
            if prop=='lastIndexOf': return lambda *a:obj.rfind(a[0]) if a else -1
            if prop=='slice':       return lambda *a:self._str_slice(obj,*a)
            if prop=='substring':   return lambda *a:obj[max(0,int(a[0])):int(a[1]) if len(a)>1 else len(obj)]
            if prop=='replace':     return lambda *a:self._str_replace(obj,a[0],a[1]) if len(a)>=2 else obj
            if prop=='replaceAll':  return lambda *a:obj.replace(str(a[0]),str(a[1])) if len(a)>=2 else obj
            if prop=='repeat':      return lambda *a:obj*max(0,int(a[0])) if a else obj
            if prop=='charAt':      return lambda *a:obj[int(a[0])] if a and 0<=int(a[0])<len(obj) else ''
            if prop=='charCodeAt':  return lambda *a:ord(obj[int(a[0])]) if a and 0<=int(a[0])<len(obj) else float('nan')
            if prop=='padStart':    return lambda *a:obj.rjust(int(a[0]),str(a[1]) if len(a)>1 else ' ') if a else obj
            if prop=='padEnd':      return lambda *a:obj.ljust(int(a[0]),str(a[1]) if len(a)>1 else ' ') if a else obj
            if prop=='toString':    return lambda *a:obj
            if prop=='valueOf':     return lambda *a:obj
            if prop=='at':          return lambda *a:obj[int(a[0]) if int(a[0])>=0 else len(obj)+int(a[0])] if a and abs(int(a[0]))<len(obj) else 'undefined'
            if prop=='match':       return lambda *a:self._str_match(obj,a[0]) if a else None
            if prop=='matchAll':    return lambda *a:[[m.group(0)]+list(m.groups()) for m in re.finditer(str(a[0]),obj)] if a else []
            if prop=='search':      return lambda *a:obj.find(str(a[0])) if a else -1
            if prop=='normalize':   return lambda *a:obj
            try:
                idx=int(prop)
                return obj[idx] if 0<=idx<len(obj) else 'undefined'
            except: pass
            return 'undefined'

        if isinstance(obj,(int,float)):
            if prop=='toString': return lambda *a:self._js_str(obj)
            if prop=='toFixed':  return lambda *a:f"{obj:.{int(a[0]) if a else 0}f}"
            if prop=='toLocaleString': return lambda *a:f"{obj:,}"
            return 'undefined'

        if isinstance(obj,dict):
            k=str(prop)
            v=obj.get(k,'undefined')
            if v=='undefined':
                if k=='hasOwnProperty': return lambda *a:(str(a[0]) in obj) if a else False
                if k=='toString': return lambda *a:'[object Object]'
                if k=='valueOf': return lambda *a:obj
            return v

        if callable(obj) and hasattr(obj,prop):
            return getattr(obj,prop)

        return 'undefined'

    def eval_call(self,node,env):
        expanded=self._eval_args(node.args,env)
        this_obj=None
        if isinstance(node.callee,MemberExpr):
            this_obj=self.eval(node.callee.obj,env)
            prop=node.callee.prop if not node.callee.computed else self._js_str(self.eval(node.callee.prop,env))
            if callable(this_obj) and hasattr(this_obj,prop):
                fn=getattr(this_obj,prop)
            else:
                fn=self.eval_member(node.callee,env,obj=this_obj)
        else:
            fn=self.eval(node.callee,env)
        # Task 1: TypeError for non-callable
        if fn=='undefined' or fn is None:
            name='unknown'
            if isinstance(node.callee,Identifier): name=node.callee.name
            elif isinstance(node.callee,MemberExpr):
                name=node.callee.prop if not node.callee.computed else '...'
            raise ThrowSignal(JSTypeError(f'{name} is not a function'))
        if callable(fn): return fn(*expanded)
        if isinstance(fn,JSFunction): return self._call_fn(fn,expanded,this_obj)
        name='unknown'
        if isinstance(node.callee,Identifier): name=node.callee.name
        raise ThrowSignal(JSTypeError(f'{name} is not a function'))

    def _eval_args(self,args,env):
        r=[]
        for a in args:
            if isinstance(a,SpreadElement):
                v=self.eval(a.argument,env)
                if isinstance(v,JSSet): r.extend(v._items)
                elif isinstance(v,JSMap): r.extend(v._entries_iter())
                elif isinstance(v,list): r.extend(v)
            else: r.append(self.eval(a,env))
        return r

    def _call_fn(self,fn,args,this_obj=None):
        fe=Environment(fn.closure)
        if fn.name: fe.define(fn.name,fn)
        if this_obj is not None: fe.define('this',this_obj)
        for i,p in enumerate(fn.params):
            if p.rest: fe.define(p.name,args[i:]); break
            v=args[i] if i<len(args) else 'undefined'
            if v=='undefined' and p.default is not None:
                v=self.eval(p.default,fe)
            fe.define(p.name,v)

        def _exec():
            if isinstance(fn.body,BlockStmt):
                for s in fn.body.body:
                    if isinstance(s,FuncDecl):
                        fe.define(s.name,JSFunction(s.name,s.params,s.body,fe))
                try:
                    for s in fn.body.body:
                        if not isinstance(s,FuncDecl): self.exec_stmt(s,fe)
                    return 'undefined'
                except ReturnSignal as r: return r.value
            else:
                return self.eval(fn.body,fe)

        if fn.is_async:
            p=JSPromise(self)
            if isinstance(fn.body,BlockStmt):
                self._run_async_stmts(p,fe,fn.body.body,0)
            else:
                try:
                    res=self.eval(fn.body,fe)
                    if isinstance(res,JSPromise): res._add_then(p.resolve,p.reject)
                    else: p.resolve(res)
                except AwaitSuspend as aws:
                    def _on_f(val):
                        if isinstance(val,JSPromise): val._add_then(p.resolve,p.reject)
                        else: p.resolve(val)
                    def _on_r(reason): p.reject(reason)
                    if aws.promise.state==JSPromise.FULFILLED:
                        self._microtask_queue.append((_on_f,[aws.promise.value]))
                    elif aws.promise.state==JSPromise.REJECTED:
                        self._microtask_queue.append((_on_r,[aws.promise.reason]))
                    else: aws.promise._add_then(_on_f,_on_r)
                except ThrowSignal as e: p.reject(e.value)
                except Exception as e: p.reject(str(e))
            return p
        return _exec()
    
    def _run_async_stmts(self,result_p,env,stmts,start_idx):
        """Execute async function body with true suspension at each await."""
        if start_idx==0:                          # hoist func decls on first entry
            for s in stmts:
                if isinstance(s,FuncDecl):
                    env.define(s.name,JSFunction(s.name,s.params,s.body,env))
        try:
            for i in range(start_idx,len(stmts)):
                s=stmts[i]
                if isinstance(s,FuncDecl): continue
                try:
                    self.exec_stmt(s,env)
                except AwaitSuspend as aws:
                    # Suspend here; schedule the rest as a microtask
                    rfn=aws.resume_fn
                    is_ret=isinstance(s,ReturnStmt)
                    interp=self; rp=result_p; e=env
                    def _mk(nxt,rfn2,iret,ss):
                        def on_f(val):
                            if rfn2:
                                try: rfn2(val)
                                except ReturnSignal as r: rp.resolve(r.value); return
                                except ThrowSignal as ex: rp.reject(ex.value); return
                            if iret: rp.resolve(val); return
                            interp._run_async_stmts(rp,e,ss,nxt)
                        def on_r(reason): rp.reject(reason)
                        return on_f,on_r
                    on_f,on_r=_mk(i+1,rfn,is_ret,stmts)
                    prom=aws.promise
                    if prom.state==JSPromise.FULFILLED:
                        self._microtask_queue.append((on_f,[prom.value]))
                    elif prom.state==JSPromise.REJECTED:
                        self._microtask_queue.append((on_r,[prom.reason]))
                    else: prom._add_then(on_f,on_r)
                    return   # ← actual suspension point
            result_p.resolve('undefined')
        except ReturnSignal as r: result_p.resolve(r.value)
        except ThrowSignal as e: result_p.reject(e.value)
        except Exception as e: result_p.reject(str(e))

    def _arr_join(self,arr,sep=','):
        if sep is None: sep=','
        return sep.join('' if x is None or x=='undefined' else self._js_str(x) for x in arr)

    def _arr_slice(self,arr,*a):
        s=int(a[0]) if a else 0
        e=int(a[1]) if len(a)>1 else len(arr)
        if s<0: s=max(0,len(arr)+s)
        if e<0: e=max(0,len(arr)+e)
        return arr[s:e]

    def _arr_splice(self,arr,*a):
        if not a: return []
        start=int(a[0])
        if start<0: start=max(0,len(arr)+start)
        start=min(start,len(arr))
        dc=int(a[1]) if len(a)>1 else len(arr)-start
        items=list(a[2:]) if len(a)>2 else []
        removed=arr[start:start+dc]
        arr[start:start+dc]=items
        return removed

    def _arr_sort(self,arr,fn=None):
        import functools
        if fn is None:
            arr.sort(key=lambda x:self._js_str(x))
        else:
            def cmp(a,b):
                r=self._call_fn(fn,[a,b]) if isinstance(fn,JSFunction) else fn(a,b)
                return self._num(r)
            arr.sort(key=functools.cmp_to_key(cmp))
        return arr

    def _call_cb(self,fn,args):
        if isinstance(fn,JSFunction): return self._call_fn(fn,args)
        if callable(fn): return fn(*args)
        return 'undefined'

    def _arr_map(self,arr,fn):
        return [self._call_cb(fn,[item,i,arr]) for i,item in enumerate(arr)]

    def _arr_filter(self,arr,fn):
        return [item for i,item in enumerate(arr) if self._bool(self._call_cb(fn,[item,i,arr]))]

    def _arr_reduce(self,arr,fn,init=None):
        if not arr: return init
        start=0; acc=init
        if init is None: acc=arr[0]; start=1
        for i in range(start,len(arr)): acc=self._call_cb(fn,[acc,arr[i],i,arr])
        return acc

    def _arr_find(self,arr,fn):
        for i,item in enumerate(arr):
            if self._bool(self._call_cb(fn,[item,i,arr])): return item
        return 'undefined'

    def _find_idx(self,arr,fn):
        for i,item in enumerate(arr):
            if self._bool(self._call_cb(fn,[item,i,arr])): return i
        return -1

    def _arr_some(self,arr,fn):
        for i,item in enumerate(arr):
            if self._bool(self._call_cb(fn,[item,i,arr])): return True
        return False

    def _arr_every(self,arr,fn):
        for i,item in enumerate(arr):
            if not self._bool(self._call_cb(fn,[item,i,arr])): return False
        return True

    def _arr_flat(self,arr,depth=1):
        r=[]
        for item in arr:
            if isinstance(item,list) and depth>0: r.extend(self._arr_flat(item,depth-1))
            else: r.append(item)
        return r

    def _arr_flatmap(self,arr,fn):
        r=[]
        for i,item in enumerate(arr):
            m=self._call_cb(fn,[item,i,arr])
            if isinstance(m,list): r.extend(m)
            else: r.append(m)
        return r

    def _arr_foreach(self,arr,fn):
        for i,item in enumerate(arr): self._call_cb(fn,[item,i,arr])
        return 'undefined'

    def _arr_fill(self,arr,*a):
        v=a[0] if a else 'undefined'
        s=int(a[1]) if len(a)>1 else 0
        e=int(a[2]) if len(a)>2 else len(arr)
        for i in range(s,e): arr[i]=v
        return arr

    def _str_slice(self,s,*a):
        start=int(a[0]) if a else 0
        end=int(a[1]) if len(a)>1 else len(s)
        if start<0: start=max(0,len(s)+start)
        if end<0: end=max(0,len(s)+end)
        return s[start:end]

    def _str_replace(self,s,pat,rep):
        if isinstance(rep,JSFunction):
            def repl(m): return self._js_str(self._call_fn(rep,[m.group(0)]))
            try: return re.sub(re.escape(str(pat)),repl,s,count=1)
            except: return s.replace(str(pat),str(rep),1)
        return s.replace(str(pat),str(rep),1)

    def _str_match(self,s,pat):
        try:
            m=re.search(str(pat),s)
            if m: return [m.group(0)]+list(m.groups())
            return None
        except: return None


# ═══════════════════════════════════════════
#  ENTRY
# ═══════════════════════════════════════════
def run(src):
    try:
        lexer=Lexer(src); tokens=lexer.tokenize()
        parser=Parser(tokens); ast=parser.parse()
        interp=Interpreter(); interp.exec(ast)
    except ThrowSignal as e:
        print(str(e.value),file=sys.stderr)
        sys.exit(1)
    except SystemExit: raise
    except Exception as e:
        print(str(e),file=sys.stderr)
        sys.exit(1)

if __name__=='__main__':
    if len(sys.argv)<2:
        print('Usage: python final.py <file.js>')
        print("Example:")
        print("  1. Create a JavaScript file (e.g., main.js) in the same folder.")
        print("  2. Add your JavaScript code to that file.")
        print("  3. Run: python final.py main.js")
        sys.exit(1)
    with open(sys.argv[1],'r',encoding='utf-8') as f:
        src=f.read()
    run(src)
